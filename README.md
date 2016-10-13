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
	
  You can check if you hace the right permission using AWS CLI:

  ```
  aws ec2 --region eu-west-1 describe-instances
  ```

4. Make sure you have ``zabbix-sender`` installed.

5. Add required jobs to the ``zabbix`` user crontab. This will send AWS metrics through Zabbix Sender:
  ```
  * * *  * * root . /usr/local/lib/zabbix-aws-status/bin/activate && /usr/local/bin/zabbix-aws-status.py -r eu-west-1 -o owner-id send -c /etc/zabbix/zabbix_agentd.conf > /dev/null 2>&1
  ```
  * Change ``owner-id`` to your AWS Owner ID.
  * It's recommended that you add one cron job per used region so you can avoid trying to get data from unused regions.

6. Import the template ``template-aws-status.xml``.

7. Link the host where the configured Zabbix agent is running to the template (``Template AWS Status``). You need to configure the following macro in the host:
  * ``{$OWNER_ID}``: Comma separated AWS owner ID values. This is needed, for example, to avoid listing all public snapshots.

# Example output data

This is a sample of the data that can be retrieved by zabbix-aws-status into Zabbix:
 
 * This information is per region
 * State statistics per instance type and total.
 * Snapshot statistics: number, state, total size.
 * Volume statistics: number, state, total size.

```
aws.stats["eu-west-1","addresses.allocated"]
aws.stats["eu-west-1","addresses.total"]
aws.stats["eu-west-1","instances.monitoring.disabled"]
aws.stats["eu-west-1","instances.monitoring.enabled"]
aws.stats["eu-west-1","instances.state.pending"]
aws.stats["eu-west-1","instances.state.running"]
aws.stats["eu-west-1","instances.state.shutting-down"]
aws.stats["eu-west-1","instances.state.stopped"]
aws.stats["eu-west-1","instances.state.stopping"]
aws.stats["eu-west-1","instances.state.terminated"]
aws.stats["eu-west-1","instances.type.m1_medium.pending"]
aws.stats["eu-west-1","instances.type.m1_medium.running"]
aws.stats["eu-west-1","instances.type.m1_medium.shutting-down"]
aws.stats["eu-west-1","instances.type.m1_medium.stopped"]
aws.stats["eu-west-1","instances.type.m1_medium.stopping"]
aws.stats["eu-west-1","instances.type.m1_medium.terminated"]
aws.stats["eu-west-1","instances.type.m1_medium.total"]
aws.stats["eu-west-1","instances.type.m1_small.pending"]
aws.stats["eu-west-1","instances.type.m1_small.running"]
aws.stats["eu-west-1","instances.type.m1_small.shutting-down"]
aws.stats["eu-west-1","instances.type.m1_small.stopped"]
aws.stats["eu-west-1","instances.type.m1_small.stopping"]
aws.stats["eu-west-1","instances.type.m1_small.terminated"]
aws.stats["eu-west-1","instances.type.m1_small.total"]
aws.stats["eu-west-1","instances.type.m2_4xlarge.pending"]
aws.stats["eu-west-1","instances.type.m2_4xlarge.running"]
aws.stats["eu-west-1","instances.type.m2_4xlarge.shutting-down"]
aws.stats["eu-west-1","instances.type.m2_4xlarge.stopped"]
aws.stats["eu-west-1","instances.type.m2_4xlarge.stopping"]
aws.stats["eu-west-1","instances.type.m2_4xlarge.terminated"]
aws.stats["eu-west-1","instances.type.m2_4xlarge.total"]
aws.stats["eu-west-1","instances.type.m3_2xlarge.pending"]
aws.stats["eu-west-1","instances.type.m3_2xlarge.running"]
aws.stats["eu-west-1","instances.type.m3_2xlarge.shutting-down"]
aws.stats["eu-west-1","instances.type.m3_2xlarge.stopped"]
aws.stats["eu-west-1","instances.type.m3_2xlarge.stopping"]
aws.stats["eu-west-1","instances.type.m3_2xlarge.terminated"]
aws.stats["eu-west-1","instances.type.m3_2xlarge.total"]
aws.stats["eu-west-1","instances.type.m3_medium.pending"]
aws.stats["eu-west-1","instances.type.m3_medium.running"]
aws.stats["eu-west-1","instances.type.m3_medium.shutting-down"]
aws.stats["eu-west-1","instances.type.m3_medium.stopped"]
aws.stats["eu-west-1","instances.type.m3_medium.stopping"]
aws.stats["eu-west-1","instances.type.m3_medium.terminated"]
aws.stats["eu-west-1","instances.type.m3_medium.total"]
aws.stats["eu-west-1","instances.type.m4_large.pending"]
aws.stats["eu-west-1","instances.type.m4_large.running"]
aws.stats["eu-west-1","instances.type.m4_large.shutting-down"]
aws.stats["eu-west-1","instances.type.m4_large.stopped"]
aws.stats["eu-west-1","instances.type.m4_large.stopping"]
aws.stats["eu-west-1","instances.type.m4_large.terminated"]
aws.stats["eu-west-1","instances.type.m4_large.total"]
aws.stats["eu-west-1","instances.type.t1_micro.pending"]
aws.stats["eu-west-1","instances.type.t1_micro.running"]
aws.stats["eu-west-1","instances.type.t1_micro.shutting-down"]
aws.stats["eu-west-1","instances.type.t1_micro.stopped"]
aws.stats["eu-west-1","instances.type.t1_micro.stopping"]
aws.stats["eu-west-1","instances.type.t1_micro.terminated"]
aws.stats["eu-west-1","instances.type.t1_micro.total"]
aws.stats["eu-west-1","instances.type.t2_medium.pending"]
aws.stats["eu-west-1","instances.type.t2_medium.running"]
aws.stats["eu-west-1","instances.type.t2_medium.shutting-down"]
aws.stats["eu-west-1","instances.type.t2_medium.stopped"]
aws.stats["eu-west-1","instances.type.t2_medium.stopping"]
aws.stats["eu-west-1","instances.type.t2_medium.terminated"]
aws.stats["eu-west-1","instances.type.t2_medium.total"]
aws.stats["eu-west-1","instances.type.t2_micro.pending"]
aws.stats["eu-west-1","instances.type.t2_micro.running"]
aws.stats["eu-west-1","instances.type.t2_micro.shutting-down"]
aws.stats["eu-west-1","instances.type.t2_micro.stopped"]
aws.stats["eu-west-1","instances.type.t2_micro.stopping"]
aws.stats["eu-west-1","instances.type.t2_micro.terminated"]
aws.stats["eu-west-1","instances.type.t2_micro.total"]
aws.stats["eu-west-1","instances.type.t2_nano.pending"]
aws.stats["eu-west-1","instances.type.t2_nano.running"]
aws.stats["eu-west-1","instances.type.t2_nano.shutting-down"]
aws.stats["eu-west-1","instances.type.t2_nano.stopped"]
aws.stats["eu-west-1","instances.type.t2_nano.stopping"]
aws.stats["eu-west-1","instances.type.t2_nano.terminated"]
aws.stats["eu-west-1","instances.type.t2_nano.total"]
aws.stats["eu-west-1","instances.type.t2_small.pending"]
aws.stats["eu-west-1","instances.type.t2_small.running"]
aws.stats["eu-west-1","instances.type.t2_small.shutting-down"]
aws.stats["eu-west-1","instances.type.t2_small.stopped"]
aws.stats["eu-west-1","instances.type.t2_small.stopping"]
aws.stats["eu-west-1","instances.type.t2_small.terminated"]
aws.stats["eu-west-1","instances.type.t2_small.total"]
aws.stats["eu-west-1","snapshots.size"]
aws.stats["eu-west-1","snapshots.state.completed"]
aws.stats["eu-west-1","snapshots.state.error"]
aws.stats["eu-west-1","snapshots.state.pending"]
aws.stats["eu-west-1","volumes.size"]
aws.stats["eu-west-1","volumes.state.available"]
aws.stats["eu-west-1","volumes.state.creating"]
aws.stats["eu-west-1","volumes.state.deleted"]
aws.stats["eu-west-1","volumes.state.deleting"]
aws.stats["eu-west-1","volumes.state.error"]
aws.stats["eu-west-1","volumes.state.in-use"]

```
