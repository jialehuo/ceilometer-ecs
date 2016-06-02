===============================
ceilometer-ecs
===============================

ECS Custom Meters for Ceilometer

This package provides files used by OpenStack Ceilometer to monitor the
usage meters of ECS instances. With this package installed
and configured, the Ceilometer Central Agent will poll remote ECS instances
via REST API, and store the results as meters with the name 'ecs.*'.

* Free software: Apache license

Features
--------

This module enables polling of ECS instances to collect usage information 

Enabling In DevStack
--------------------

To enable use of ECS Ceilometer meters in DevStack, add this repository as
a plugin:

     enable_plugin ceilometer-ecs https://hwstashprd01.isus.emc.com:8443/scm/naoil/ceilometer-ecs.git
     enable_service ceilometer-ecs

Installation
-----------------------

This module has the following dependancies:

1. NTP: this module relies on accurate time to decide when to poll remote ECS instances, so NTP is required on the server. To enable NTP, follow the steps below, for example.

sudo ntpdate <time.server.ip.address>
sudo apt install ntp
sudo vi /etc/ntp.conf (add NTP servers)
sudo service ntp restart
ntpq -p (verify NTP status)

2. Python packages: this module relies on additional Python packages that are not installed on DevStack by default. Follow the steps below to install them.

sudo pip install --upgrade ndg-httpsclient
sudo pip install python-dateutil iso8601

3. ECS management REST API certificate: to make calls to poll ECS meters, a certificate has to be installed on the server running the module. Refer to ECS documentation on how to find the certificate. Once found, simply copy the certificate onto the server, and set the location in the configuration parameters of the module (detailed below in the Configuration section).

4. Install: 

cd <ceilometer-ecs.dir>
sudo python setup.py install

Configuration
-----------------------

The following section have to be appended to /etc/ceilometer/ceilometer.conf

[ecs]
ecs_endpoint = <ECS endpoint, e.g., https://10.1.83.51:4443>
ecs_username = <ECS username, e.g., admin>
ecs_password = <ECS password, e.g., secret>
ecs_cert_path = <path to the ECS management REST API certificate, e.g., /opt/stack/ecs-mgmt.cer>
ceilometer_endpoint = <endpoint to Ceilometer v2 API, e.g., http://127.0.0.1:8777>
os_username = <OpenStack username, e.g., admin>
os_password = <OpenStack password, e.g., secret>
os_user_domain_name = <OpenStack domain name for the user, e.g., Default>
os_project_name = <OpenStack project name for the user, e.g., demo>
os_project_domain_name = <OpenStack domain name for the project, e.g., Default>
os_auth_url = <OpenStack authentication URL, e.g., http://127.0.0.1/identity>
sample_start_time = <start time for sampling, in ISO8601 format, e.g., 2016-05-27T12:00:00Z>
sample_interval = <sampling interval in minutes, e.g., 60>
sample_delay = <delay to the end time for sampling. Samples are polled after sample_start_time + sample_interval + sample_delay, e.g., 30>

Note
-----------------------

1. The module's sampling behavior can do "catch up", i.e., it samples meters from the past if sample_start_time is set to the past. By default, the ECSBillingPoller is run every 10 minutes, when it checks if it's time to poll ECS for meters, and if yes, it polls the meters. The frequency to run ECSBillingPoller can be changed by editing /etc/ceilometer/pipeline.yaml, and add the following text to the 'sources' section:

    - name: ecs_source
      interval: <interval to run the poller in seconds>
      meters:
          - "ecs.objects"
      sinks:
          - meter_sink

2. The frequency to poll ECS for meters is actually defined by 'sample_interval' parameter defined in the config file /etc/ceilometer/ceilometer.conf

3. The Ceilometer and OpenStack config info are needed to access the Ceilometer API to find out the last sample end time, which is also the next sample start time. ECS meters are retrieved with a 'sample_start_time' and a 'sample_end_time' timestamp, and the Ceilometer API is the only way to find out previous polling information without creating persistent cache on the disk. The OpenStack project and user information are used to authenticate against Keystone to gain access the Ceilometer API.
