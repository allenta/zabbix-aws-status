# Zabbix AWS Status

## Requirements

* Python 3
* [AWS SDK for Python 3](https://aws.amazon.com/sdk-for-python/)
* [Zabbix sender](https://www.zabbix.com/documentation/3.0/manual/concepts/sender)

## Installation

1. Copy ``zabbix-aws-status.py`` to ``/usr/local/bin/``, and make it executable.

2. Install AWS SDK for Python3 using Virtualenv or an equivalent method:

  ```
  # virtualenv --python=python3 /usr/local/lib/zabbix-aws-status
  ```
  
3. Add the ``awsstats.discovery`` user parameters to Zabbix agent. This agent must have permissions to access the AWS API through instance role or AccessKey/SecretKey pair:

  ```
  UserParameter=awsstats.discovery[*],. /usr/local/lib/zabbix-aws-status/bin/activate && /usr/local/bin/zabbix-aws-status.py -r '$1' -o '$2' discover $3
  ```
	
  You can check if you have the right permissions using [AWS CLI](https://aws.amazon.com/cli/):

  ```
  $ aws ec2 --region eu-west-1 describe-instances
  $ aws ec2 --region eu-west-1 describe-snapshots
  $ aws ec2 --region eu-west-1 describe-volumes
  ```

4. Make sure you have ``zabbix-sender`` installed.

5. Add required jobs to the ``zabbix`` user crontab. This will send AWS metrics through Zabbix Sender:
  ```
  * * *  * * root . /usr/local/lib/zabbix-aws-status/bin/activate && /usr/local/bin/zabbix-aws-status.py -r global -o owner-id send -c /etc/zabbix/zabbix_agentd.conf > /dev/null 2>&1
  * * *  * * root . /usr/local/lib/zabbix-aws-status/bin/activate && /usr/local/bin/zabbix-aws-status.py -r eu-west-1 -o owner-id send -c /etc/zabbix/zabbix_agentd.conf > /dev/null 2>&1
  ```
  * Change ``owner-id`` to your AWS Owner ID.
  * It's recommended that you add one cron job per used region so you can avoid trying to get data from unused regions.
  * Note the first cron job uses "global" as region. This is used to fetch information about resources that don't depend on a region, like S3.

6. Import the template ``template-aws-status.xml``.

7. Link the host where the configured Zabbix agent is running to the template (``Template AWS Status``). You need to configure the following macro in the host:
  * ``{$OWNER_ID}``: Comma separated AWS owner ID values. This is needed, for example, to avoid listing all public snapshots.

# Example output data

This is a sample of the data that can be retrieved by zabbix-aws-status into Zabbix:
 
## Per region information

 * State statistics per instance type and total.
 * Snapshot statistics: number, state, total size.
 * Volume statistics: number, state, total size.
 * ElasticIPs: total and allocated.

```
aws.stats["owner-id","eu-west-1","addresses.allocated"]
aws.stats["owner-id","eu-west-1","addresses.total"]
aws.stats["owner-id","eu-west-1","instances.monitoring.disabled"]
aws.stats["owner-id","eu-west-1","instances.monitoring.enabled"]
aws.stats["owner-id","eu-west-1","instances.state.pending"]
aws.stats["owner-id","eu-west-1","instances.state.running"]
aws.stats["owner-id","eu-west-1","instances.state.shutting-down"]
aws.stats["owner-id","eu-west-1","instances.state.stopped"]
aws.stats["owner-id","eu-west-1","instances.state.stopping"]
aws.stats["owner-id","eu-west-1","instances.state.terminated"]
aws.stats["owner-id","eu-west-1","instances.type.m1_small.pending"]
aws.stats["owner-id","eu-west-1","instances.type.m1_small.running"]
aws.stats["owner-id","eu-west-1","instances.type.m1_small.shutting-down"]
aws.stats["owner-id","eu-west-1","instances.type.m1_small.stopped"]
aws.stats["owner-id","eu-west-1","instances.type.m1_small.stopping"]
aws.stats["owner-id","eu-west-1","instances.type.m1_small.terminated"]
aws.stats["owner-id","eu-west-1","instances.type.m1_small.total"]
aws.stats["owner-id","eu-west-1","instances.type.m2_4xlarge.pending"]
aws.stats["owner-id","eu-west-1","instances.type.m2_4xlarge.running"]
aws.stats["owner-id","eu-west-1","instances.type.m2_4xlarge.shutting-down"]
aws.stats["owner-id","eu-west-1","instances.type.m2_4xlarge.stopped"]
aws.stats["owner-id","eu-west-1","instances.type.m2_4xlarge.stopping"]
aws.stats["owner-id","eu-west-1","instances.type.m2_4xlarge.terminated"]
aws.stats["owner-id","eu-west-1","instances.type.m2_4xlarge.total"]
aws.stats["owner-id","eu-west-1","instances.type.m3_2xlarge.pending"]
aws.stats["owner-id","eu-west-1","instances.type.m3_2xlarge.running"]
aws.stats["owner-id","eu-west-1","instances.type.m3_2xlarge.shutting-down"]
aws.stats["owner-id","eu-west-1","instances.type.m3_2xlarge.stopped"]
aws.stats["owner-id","eu-west-1","instances.type.m3_2xlarge.stopping"]
aws.stats["owner-id","eu-west-1","instances.type.m3_2xlarge.terminated"]
aws.stats["owner-id","eu-west-1","instances.type.m3_2xlarge.total"]
aws.stats["owner-id","eu-west-1","instances.type.m3_medium.pending"]
aws.stats["owner-id","eu-west-1","instances.type.m3_medium.running"]
aws.stats["owner-id","eu-west-1","instances.type.m3_medium.shutting-down"]
aws.stats["owner-id","eu-west-1","instances.type.m3_medium.stopped"]
aws.stats["owner-id","eu-west-1","instances.type.m3_medium.stopping"]
aws.stats["owner-id","eu-west-1","instances.type.m3_medium.terminated"]
aws.stats["owner-id","eu-west-1","instances.type.m3_medium.total"]
aws.stats["owner-id","eu-west-1","instances.type.m4_large.pending"]
aws.stats["owner-id","eu-west-1","instances.type.m4_large.running"]
aws.stats["owner-id","eu-west-1","instances.type.m4_large.shutting-down"]
aws.stats["owner-id","eu-west-1","instances.type.m4_large.stopped"]
aws.stats["owner-id","eu-west-1","instances.type.m4_large.stopping"]
aws.stats["owner-id","eu-west-1","instances.type.m4_large.terminated"]
aws.stats["owner-id","eu-west-1","instances.type.m4_large.total"]
aws.stats["owner-id","eu-west-1","instances.type.t1_micro.pending"]
aws.stats["owner-id","eu-west-1","instances.type.t1_micro.running"]
aws.stats["owner-id","eu-west-1","instances.type.t1_micro.shutting-down"]
aws.stats["owner-id","eu-west-1","instances.type.t1_micro.stopped"]
aws.stats["owner-id","eu-west-1","instances.type.t1_micro.stopping"]
aws.stats["owner-id","eu-west-1","instances.type.t1_micro.terminated"]
aws.stats["owner-id","eu-west-1","instances.type.t1_micro.total"]
aws.stats["owner-id","eu-west-1","instances.type.t2_medium.pending"]
aws.stats["owner-id","eu-west-1","instances.type.t2_medium.running"]
aws.stats["owner-id","eu-west-1","instances.type.t2_medium.shutting-down"]
aws.stats["owner-id","eu-west-1","instances.type.t2_medium.stopped"]
aws.stats["owner-id","eu-west-1","instances.type.t2_medium.stopping"]
aws.stats["owner-id","eu-west-1","instances.type.t2_medium.terminated"]
aws.stats["owner-id","eu-west-1","instances.type.t2_medium.total"]
aws.stats["owner-id","eu-west-1","instances.type.t2_micro.pending"]
aws.stats["owner-id","eu-west-1","instances.type.t2_micro.running"]
aws.stats["owner-id","eu-west-1","instances.type.t2_micro.shutting-down"]
aws.stats["owner-id","eu-west-1","instances.type.t2_micro.stopped"]
aws.stats["owner-id","eu-west-1","instances.type.t2_micro.stopping"]
aws.stats["owner-id","eu-west-1","instances.type.t2_micro.terminated"]
aws.stats["owner-id","eu-west-1","instances.type.t2_micro.total"]
aws.stats["owner-id","eu-west-1","instances.type.t2_nano.pending"]
aws.stats["owner-id","eu-west-1","instances.type.t2_nano.running"]
aws.stats["owner-id","eu-west-1","instances.type.t2_nano.shutting-down"]
aws.stats["owner-id","eu-west-1","instances.type.t2_nano.stopped"]
aws.stats["owner-id","eu-west-1","instances.type.t2_nano.stopping"]
aws.stats["owner-id","eu-west-1","instances.type.t2_nano.terminated"]
aws.stats["owner-id","eu-west-1","instances.type.t2_nano.total"]
aws.stats["owner-id","eu-west-1","instances.type.t2_small.pending"]
aws.stats["owner-id","eu-west-1","instances.type.t2_small.running"]
aws.stats["owner-id","eu-west-1","instances.type.t2_small.shutting-down"]
aws.stats["owner-id","eu-west-1","instances.type.t2_small.stopped"]
aws.stats["owner-id","eu-west-1","instances.type.t2_small.stopping"]
aws.stats["owner-id","eu-west-1","instances.type.t2_small.terminated"]
aws.stats["owner-id","eu-west-1","instances.type.t2_small.total"]
aws.stats["owner-id","eu-west-1","snapshots.size"]
aws.stats["owner-id","eu-west-1","snapshots.state.completed"]
aws.stats["owner-id","eu-west-1","snapshots.state.error"]
aws.stats["owner-id","eu-west-1","snapshots.state.pending"]
aws.stats["owner-id","eu-west-1","volumes.size"]
aws.stats["owner-id","eu-west-1","volumes.state.available"]
aws.stats["owner-id","eu-west-1","volumes.state.creating"]
aws.stats["owner-id","eu-west-1","volumes.state.deleted"]
aws.stats["owner-id","eu-west-1","volumes.state.deleting"]
aws.stats["owner-id","eu-west-1","volumes.state.error"]
aws.stats["owner-id","eu-west-1","volumes.state.in-use"]
```

## Global information

 * S3: number of buckets

```
aws.stats["owner-id","global","s3.buckets"]
```

