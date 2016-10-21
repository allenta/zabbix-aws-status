#!/usr/bin/env python

'''
:url: https://github.com/allenta/zabbix-aws-status
:copyright: (c) 2016 by Allenta Consulting S.L. <info@allenta.com>.
:license: BSD, see LICENSE.txt for more details.
'''

import boto3
import collections
import argparse
import subprocess
import time
import sys
import json

import threading
from queue import Queue


REGIONS = {
    'us-east-1': 'US East (N. Virginia)',
    'us-east-2': 'US East (Ohio)',
    'us-west-2': 'US West (Oregon)',
    'us-west-1': 'US West (N. California)',
    'eu-west-1': 'EU (Ireland)',
    'eu-central-1': 'EU (Frankfurt)',
    'ap-southeast-1': 'Asia Pacific (Singapore)',
    'ap-northeast-1': 'Asia Pacific (Tokyo)',
    'ap-southeast-2': 'Asia Pacific (Sydney)',
    'ap-northeast-2': 'Asia Pacific (Seoul)',
    'ap-south-1': 'Asia Pacific (Mumbai)',
    'sa-east-1': 'South America (São Paulo)'
}

GLOBAL_REGION = 'global'

SUBJECTS = {
    'instancetypes': None,
    'regions': None,
}

# Forgive me $deity for this global
discovery = {
    'data': [],
}

# lock to serialize acces to discovery
lock = threading.Lock()
# Create the queue
q = Queue()


def flatten(d, parent_key='', separator='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + separator + str(k) if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, separator=separator).items())
        else:
            items.append((new_key, v))

    return dict(items)


def extract_data(region, owner_id=None):

    session = boto3.session.Session()

    if region != GLOBAL_REGION:

        result = {
            'instances': {
                'monitoring': {
                    'enabled': 0,
                    'disabled': 0
                },
                'state': {
                    'pending': 0,
                    'running': 0,
                    'shutting-down': 0,
                    'stopping': 0,
                    'stopped': 0,
                    'terminated': 0
                },
                'type': dict()
            },
            'addresses': {
                'allocated': 0,
                'total': 0
            },
            'snapshots': {
                'state': {
                    'completed': 0,
                    'error': 0,
                    'pending': 0
                },
                'size': 0
            },
            'volumes': {
                'state': {
                    'available': 0,
                    'creating': 0,
                    'deleted': 0,
                    'deleting': 0,
                    'error': 0,
                    'in-use': 0
                },
                'size': 0
            }
        }

        ec2 = session.resource('ec2', region_name=region)
        instances = ec2.instances.all()

        for instance in instances:

            # Instance by monitoring state
            if instance.monitoring['State'] in result['instances']['monitoring']:
                    result['instances']['monitoring'][instance.monitoring['State']] += 1
            else:
                result['instances']['monitoring'][instance.monitoring['State']] = 1

            # Instances by type
            instance_type = instance.instance_type.replace('.', '_')
            if instance_type in result['instances']['type']:
                result['instances']['type'][instance_type]['total'] += 1
            else:
                result['instances']['type'][instance_type] = {
                    'total': 1,
                    'pending': 0,
                    'running': 0,
                    'shutting-down': 0,
                    'stopping': 0,
                    'stopped': 0,
                    'terminated': 0
                }

            # Instances state by type
            result['instances']['type'][instance_type][instance.state['Name']] += 1

            # Instances by state
            if instance.state['Name'] in result['instances']['state']:
                result['instances']['state'][instance.state['Name']] += 1
            else:
                result['instances']['state'][instance.state['Name']] = 1

        ec2_client = session.client('ec2', region_name=region)

        # Allocated and total ElasticIPs
        addresses = ec2_client.describe_addresses()
        for address in addresses['Addresses']:
            if address.get('AllocationId'):
                result['addresses']['allocated'] += 1
            if address.get('PublicIp'):
                result['addresses']['total'] += 1

        # Create filter to avoid listing all public snapshots
        if owner_id:
            resource_filter = [{
                'Name': 'owner-id',
                'Values': owner_id.split(',')
            }]
        else:
            resource_filter = []

        snapshots = ec2.snapshots.filter(Filters=resource_filter)

        for s in snapshots:
            if s.state in result['snapshots']['state']:
                result['snapshots']['state'][s.state] += 1
            else:
                result['snapshots']['state'][s.state] = 1

            result['snapshots']['size'] += s.volume_size

        volumes = ec2.volumes.all()

        for v in volumes:
            if v.state in result['volumes']['state']:
                result['volumes']['state'][v.state] += 1
            else:
                result['volumes']['state'][v.state] = 1

            result['volumes']['size'] += v.size

    else:
        # Global region

        result = {
            's3': {
                'buckets': 0
            }
        }

        s3 = session.resource('s3')
        buckets = s3.buckets.all()

        for b in buckets:
            result['s3']['buckets'] += 1

    return result


def discover_region(region, options):
    global discovery

    # Extract data from this region
    result = extract_data(region, owner_id=options.owner_id)

    if options.subject == 'instancetypes':

        for instance_type in set(result['instances']['type']):
            # Lock before updating
            with lock:
                discovery['data'].append({
                    '{#AWSREGION}': region,
                    '{#INSTANCETYPE}': instance_type
                })

    elif options.subject == 'regions':

        # Check if there is resources in that region
        if (result['volumes']['size'] > 0 or
                result['snapshots']['size'] > 0 or
                result['addresses']['total'] > 0 or
                result['instances']['type']):

            # Lock before updating
            with lock:
                discovery['data'].append({
                    '{#AWSREGION}': region,
                    '{#AWSREGION_NAME}': REGIONS[region]
                })


# The worker thread pulls an item from the queue and processes it
def discover_worker():
    while True:
        (region, options) = q.get()
        discover_region(region, options)
        q.task_done()


def discover(options):
    global discovery

    # Select target regions
    if options.region:
        target_regions = [options.region]
    else:
        target_regions = REGIONS.keys()

    # Thread per region
    for i in range(len(target_regions)):
        t = threading.Thread(target=discover_worker, daemon=True)
        t.start()

    # Insert target regions in the work queue
    for region in target_regions:
        q.put([region, options])

    # Block until all tasks are done
    q.join()

    sys.stdout.write(json.dumps(discovery, sort_keys=True, indent=2))


def send(options):
    now = int(time.time())

    result = flatten(extract_data(options.region, owner_id=options.owner_id))

    data = ''.encode()
    for k, v in result.items():
        row = '- aws.stats["%(owner_id)s","%(region)s","%(key)s"] %(tst)d %(value)d\n' % {
            'owner_id': options.owner_id,
            'region': options.region,
            'key': k,
            'tst': now,
            'value': v,
        }
        data += row.encode()
        sys.stdout.write(row)

    command = 'zabbix_sender -T -r -i - %(config)s %(server)s %(port)s %(host)s' % {
        'config':
            '-c "%s"' % options.zabbix_config
            if options.zabbix_config is not None else '',
        'server':
            '-z "%s"' % options.zabbix_server
            if options.zabbix_server is not None else '',
        'port':
            '-p %d' % options.zabbix_port
            if options.zabbix_port is not None else '',
        'host':
            '-s "%s"' % options.zabbix_host
            if options.zabbix_host is not None else '',
    }
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    stdout_data = process.communicate(input=data)[0]

    if process.returncode == 0:
        sys.stdout.write(stdout_data.decode('utf-8'))
    else:
        sys.stderr.write(stdout_data.decode('utf-8'))
        sys.exit(1)


def main():

    parser = argparse.ArgumentParser(
        description='Zabbix AWS Status extractor.'
    )
    parser.add_argument('-v', action='store_true', help="Increase verbosity")
    parser.add_argument('-r', '--region', dest='region',
                        type=str, required=False, default=None,
                        help='AWS region')
    parser.add_argument('-o', '--owner-id', dest='owner_id',
                        type=str, required=True, default=None,
                        help='Owner id(s). Comma separated ids.')

    subparsers = parser.add_subparsers(dest='command')

    # Set up 'send' command
    subparser = subparsers.add_parser(
        'send',
        help='submit data through Zabbix sender')
    subparser.add_argument(
        '-c', '--zabbix-config', dest='zabbix_config',
        type=str, required=False, default=None,
        help='the Zabbix agent configuration file to fetch the configuration '
             'from')
    subparser.add_argument(
        '-z', '--zabbix-server', dest='zabbix_server',
        type=str, required=False, default=None,
        help='hostname or IP address of the Zabbix server / Zabbix proxy')
    subparser.add_argument(
        '-p', '--zabbix-port', dest='zabbix_port',
        type=int, required=False, default=None,
        help='port number of server trapper running on the Zabbix server / '
             'Zabbix proxy')
    subparser.add_argument(
        '-s', '--zabbix-host', dest='zabbix_host',
        type=str, required=False, default=None,
        help='host name as registered in the Zabbix frontend')

    # Set up 'discover' command
    subparser = subparsers.add_parser(
        'discover',
        help='generate Zabbix discovery schema')
    subparser.add_argument(
        'subject', type=str, choices=SUBJECTS.keys(),
        help="dynamic resources to be discovered")

    options = parser.parse_args()

    # Check required arguments
    if options.command == 'send':
        if options.zabbix_config is None and options.zabbix_server is None:
            parser.print_help()
            sys.exit(1)

    # Execute command
    globals()[options.command](options)
    sys.exit(0)


if __name__ == "__main__":
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
