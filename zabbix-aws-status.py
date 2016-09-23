#!/usr/bin/env python

# Metrics to monitor
#  Total non-public AMI images
#  Total public AMI images
#  Total AMI images
#  EC2 Instances - Total with monitoring disabled
#  EC2 Instances - Total with monitoring disabling
#  EC2 Instances - Total with monitoring enabled
#  EC2 Instances - Total with monitoring pending
#  EC2 Instances - Total in pending state
#  EC2 Instances - Total unavailable due to InstanceInitiatedShutdown
#  EC2 Instances - Total unavailable due to InternalError (internal to instance)
#  EC2 Instances - Total unavailable due to InvalidSnapshot
#  EC2 Instances - Total unavailable due to UserInitiatedShutdown
#  EC2 Instances - Total unavailable due to VolumeLimitExceeded
#  EC2 Instances - Total unavailable due to InsufficientInstanceCapacity
#  EC2 Instances - Total unavailable due to InternalError
#  EC2 Instances - Total unavailable due to SpotInstanceTermination
#  EC2 Instances - Total in running state
#  EC2 Instances - Total in shutting-down state
#  EC2 Instances - Total in stopped state
#  EC2 Instances - Total in stopping state
#  EC2 Instances - Total in terminated state
#  EC2 Instances - Total of type c1.medium
#  EC2 Instances - Total of type c1.xlarge
#  EC2 Instances - Total of type cc1.4xlarge
#  EC2 Instances - Total of type cg1.4xlarge
#  EC2 Instances - Total of type m1.large
#  EC2 Instances - Total of type m1.medium
#  EC2 Instances - Total of type m1.small
#  EC2 Instances - Total of type m1.xlarge
#  EC2 Instances - Total of type m2.2xlarge
#  EC2 Instances - Total of type m2.4xlarge
#  EC2 Instances - Total of type m2.xlarge
#  EC2 Instances - Total of type t1.micro
#  EC2 Instances - Total without monitoring
#  EC2 Elastic IP Addresses - Total assigned to instances
#  EC2 Elastic IP Addresses - Total
#  EC2 Elastic IP Addresses - Total unassigned/free
#  EC2 Reserved Instances - Total
#  EC2 Reserved Instances - Total of type c1.medium
#  EC2 Reserved Instances - Total of type c1.xlarge
#  EC2 Reserved Instances - Total of type m1.large
#  EC2 Reserved Instances - Total of type m1.medium
#  EC2 Reserved Instances - Total of type m1.small
#  EC2 Reserved Instances - Total of type m2.2xlarge
#  EC2 Reserved Instances - Total of type m2.4xlarge
#  EC2 Reserved Instances - Total of type other
#  EC2 Snapshots - Total Size GB
#  EC2 Snapshots - Total in status completed
#  EC2 Snapshots - Total in status error
#  EC2 Snapshots - Total in status pending
#  EC2 Snapshots - Total
#  EC2 Snapshots (Amazon-owned) - Total size GB
#  EC2 Snapshots (Amazon-owned) - Total in status completed
#  EC2 Snapshots (Amazon-owned) - Total in status error
#  EC2 Snapshots (Amazon-owned) - Total in status pending
#  EC2 Snapshots (Amazon-owned) - Total
#  EC2 Snapshots (owned by others) - Total size GB
#  EC2 Snapshots (owned by others) - Total in status completed
#  EC2 Snapshots (owned by others) - Total in status error
#  EC2 Snapshots (owned by others) - Total in status pending
#  EC2 Snapshots (owned by others) - Total
#  EC2 Snapshots (self-owned) - Total size GB
#  EC2 Snapshots (self-owned) - Total in status completed
#  EC2 Snapshots (self-owned) - Total in status error
#  EC2 Snapshots (self-owned) - Total in status pending
#  EC2 Snapshots (self-owned) - Total
#  EC2 Volumes - Total in attached state
#  EC2 Volumes - Total size (GB) of volumes in attached state
#  EC2 Volumes - Total in attaching state
#  EC2 Volumes - Total size (GB) of volumes in attaching state
#  EC2 Volumes - Total in detached state
#  EC2 Volumes - Total size (GB) of volumes in detached state
#  EC2 Volumes - Total in detaching state
#  EC2 Volumes - Total size (GB) of volumes in detaching state
#  EC2 Volumes - Total in status available
#  EC2 Volumes - Total size (GB) of volumes in status available
#  EC2 Volumes - Total in status creating
#  EC2 Volumes - Total size (GB) of volumes in status creating
#  EC2 Volumes - Total in status other
#  EC2 Volumes - Total size (GB) of volumes in status other

import boto3
import collections
import argparse
import subprocess
import time
import sys
import json

# Filter only our own resources
FILTER_OWN_RESOURCES = [{
    'Name': 'owner-id',
    'Values': ['574965702452']
}]

REGIONS = {
    'us-east-1': 'US East (N. Virginia)',
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

SUBJECTS = {
    'instancetypes': None,
    'regions': None,
}


def flatten(d, parent_key='', separator='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + separator + str(k) if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, separator=separator).items())
        else:
            items.append((new_key, v))

    return dict(items)


def extract_data(region):

    ec2 = boto3.resource('ec2', region_name=region)

    result = {
        'instances': {
            'monitoring': dict(),
            'state': dict(),
            'type': dict()
        },
        'addresses': {
            'allocated': 0,
            'total': 0
        },
        'snapshots': {
            'state': dict(),
            'size': 0
        },
        'volumes': {
            'state': dict(),
            'size': 0
        }
    }

    instances = ec2.instances.all()

    for instance in instances:
        if instance.monitoring['State'] in result['instances']['monitoring']:
                result['instances']['monitoring'][instance.monitoring['State']] += 1
        else:
            result['instances']['monitoring'][instance.monitoring['State']] = 1

        if instance.state['Name'] in result['instances']['state']:
            result['instances']['state'][instance.state['Name']] += 1
        else:
            result['instances']['state'][instance.state['Name']] = 1

        instance_type = instance.instance_type.replace('.', '_')
        if instance_type in result['instances']['type']:
            result['instances']['type'][instance_type] += 1
        else:
            result['instances']['type'][instance_type] = 1

    ec2_client = boto3.client('ec2', region_name=region)

    addresses = ec2_client.describe_addresses()
    for address in addresses['Addresses']:
        if address.get('AllocationId'):
            result['addresses']['allocated'] += 1
        if address.get('PublicIp'):
            result['addresses']['total'] += 1

    snapshots = ec2.snapshots.filter(Filters=FILTER_OWN_RESOURCES)

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

    return result


def discover(options):
    discovery = {
        'data': [],
    }

    if options.region:
        target_regions = [options.region]
    else:
        target_regions = REGIONS.keys()

    if options.subject == 'instancetypes':

        for region in target_regions:
            result = extract_data(region)

            for instance_type in set(result['instances']['type']):
                discovery['data'].append({
                    '{#AWSREGION}': region,
                    '{#INSTANCETYPE}': instance_type
                })

    elif options.subject == 'regions':

        for region in target_regions:
            result = extract_data(region)

            # Check if there is resources in that region
            if (result['volumes']['size'] > 0 or
                    result['snapshots']['size'] > 0 or
                    result['addresses']['total'] > 0 or
                    result['instances']['type']):

                discovery['data'].append({
                    '{#AWSREGION}': region,
                    '{#AWSREGION_NAME}': REGIONS[region]
                })

    sys.stdout.write(json.dumps(discovery, sort_keys=True, indent=2))


def send(options):
    now = int(time.time())

    result = flatten(extract_data(options.region))

    data = ''
    for k, v in result.items():
        row = '- aws.stat["%(region)s","%(key)s"] %(tst)d %(value)d\n' % {
            'region': options.region,
            'key': k,
            'tst': now,
            'value': v,
        }
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
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout_data = process.communicate(input=data)[0]


def main():

    parser = argparse.ArgumentParser(
        description='Zabbix AWS Status extractor.'
    )
    parser.add_argument('-v', action='store_true', help="Increase verbosity")
    parser.add_argument('-r', '--region', dest='region',
                        type=str, required=False, default=None,
                        help='AWS region')

    subparsers = parser.add_subparsers(dest='command')

    # Set up 'send' command.
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

    # Set up 'discover' command.
    subparser = subparsers.add_parser(
        'discover',
        help='generate Zabbix discovery schema')
    subparser.add_argument(
        'subject', type=str, choices=SUBJECTS.keys(),
        help="dynamic resources to be discovered")

    options = parser.parse_args()

    # Check required arguments.
    if options.command == 'send':
        if options.zabbix_config is None and options.zabbix_server is None:
            parser.print_help()
            sys.exit(1)

    # Execute command.
    globals()[options.command](options)
    sys.exit(0)


if __name__ == "__main__":
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
