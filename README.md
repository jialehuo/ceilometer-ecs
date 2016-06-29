Ceilometer-ECS
======================
This project provides Ceilometer Custom Meters for EMC's Elastic Cloud Storage (ECS).

## Description

This package provides files used by OpenStack Ceilometer to monitor the usage meters of ECS instances. With this package installed and configured, the Ceilometer Central Agent will poll remote ECS instances via REST API, and store the results as meters with the names starting with 'ecs.objects.'.

## Installation

### Pre-installation
This module has the following dependancies that must be satisfied before installation:

1. NTP: this module relies on accurate time to decide when to poll remote ECS instances, so NTP is required on the server. To enable NTP, follow the steps below on a Ubuntu server, for example.

    sudo ntpdate <time.server.ip.address>
    sudo apt install ntp
    sudo vi /etc/ntp.conf (add NTP servers)
    sudo service ntp restart
    ntpq -p (verify NTP status)

2. Python packages: this module relies on additional Python packages that are not installed on DevStack by default. Follow the steps below to install them.

    sudo pip install --upgrade ndg-httpsclient
    sudo pip install python-dateutil iso8601

3. ECS management REST API certificate: to make calls to poll ECS meters, a certificate has to be installed on the server running the module. Refer to ECS documentation on how to find the certificate. Once found, simply copy the certificate onto the server, and set the location in the configuration parameters of the module (detailed below in the Configuration section).

### DevStack
To use this project in DevStack, add this repository as a plugin:

    enable_plugin ceilometer-ecs https://github.com/jialehuo/ceilometer-ecs.git
    enable_service ceilometer-ecs

### OpenStack

Follow the following steps to install the project on OpenStack 

    cd <ceilometer-ecs.dir>
    sudo python setup.py install

### Post-installation Configuration

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

### Notes

1. The module's sampling behavior can do "catch up", i.e., it samples meters from the past if sample_start_time is set to the past. By default, the custom ECS pollers are run every 10 minutes, when they check if it's time to poll ECS for the respective meters, and if yes, they poll the meters. The frequency to run the custom ECS pollers can be changed by editing /etc/ceilometer/pipeline.yaml, and add the following text to the 'sources' section:

    - name: ecs_source
      interval: <interval to run the poller in seconds>
      meters:
          - "ecs.objects"
      sinks:
          - meter_sink

2. The frequency to poll ECS for meters is actually defined by 'sample_interval' parameter defined in the config file /etc/ceilometer/ceilometer.conf

3. The Ceilometer and OpenStack config info are needed to access the Ceilometer API to find out the last sample end time, which is also the next sample start time. ECS meters are retrieved with 'start_time' and 'end_time' timestamp, and the Ceilometer API is the only way to find out previous polling information without creating persistent cache on the disk. The OpenStack project and user information are used to authenticate against Keystone to gain access the Ceilometer API.

## Usage Instructions

Once properly installed and configured, Ceilometer-ECS should start collecting ECS usage data through Ceilometer. To see the meters, run:

    $ ceilometer meter-list

To see samples collected, run:

    $ ceilometer sample-list

To see the details of a specific sample, run:

    $ ceilometer sample-show <sample_id>

## Future

Improvements to the code structure and efficiency may come in the future.

## Contribution
Create a fork of the project into your own reposity. Make all your necessary changes and create a pull request with a description on what was added or removed and details explaining the changes in lines of code. If approved, project owners will merge it.

Licensing
---------

Ceilometer-ECS is freely distributed under the <a href="http://emccode.github.io/sampledocs/LICENSE">MIT License</a>. See LICENSE for details.

Support
-------
Please file bugs and issues at the Github issues page. For more general discussions you can contact the EMC Code team at <a href="https://groups.google.com/forum/#!forum/emccode-users">Google Groups</a> or tagged with **EMC** on <a href="https://stackoverflow.com">Stackoverflow.com</a>. The code and documentation are released with no warranties or SLAs and are intended to be supported through a community driven process.
