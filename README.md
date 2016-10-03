# Zabbix AWS Status

## Installation

1. Copy ``zabbix-aws-status`` to ``/usr/local/bin/``, and make it executable.

2. Install AWS SDK for Python3 using Virtualenv or an equivalent method:

  ```
  # virtualenv --python=python3 /usr/local/lib/zabbix-aws-status
  ```
  
3. Add the ``awsstats.discovery`` user parameters to Zabbix agent. This agent must have permissions to access the AWS API through instance role or AccessKey/SecretKey pair:

  ```
  UserParameter=awsstats.discovery[*],. /usr/local/lib/zabbix-aws-status/bin/activate && python /usr/local/bin/zabbix-aws-status.py -r '$1' -o '$2' discover $3
  ```
	
  You can check if you hace the right permission using AWS CLI:

  ```
  aws ec2 --region eu-west-1 describe-instances
  ```

4. Make sure you have ``zabbix-sender`` installed.

5. Add required jobs to the ``zabbix`` user crontab. This will send AWS metrics through Zabbix Sender:
  ```
  * * *  * * root . /usr/local/lib/zabbix-aws-status/bin/activate && python /usr/local/bin/zabbix-aws-status.py -r eu-west-1 -o 574965702452 send -c /etc/zabbix/zabbix_agentd.conf > /dev/null 2>&1
  ```
  It's recommended that you add one cron job per used region so you can avoid trying to get data from unused regions.

6. Import the template ``template-aws-status.xml``.

7. Link the host where the configured Zabbix agent is running to the template (``Template AWS Status``). You need to configure the following macro in the host:
  * ``{$OWNER_ID}``: Comma separated AWS owner ID values. This is needed, for example, to avoid listing all public snapshots.
