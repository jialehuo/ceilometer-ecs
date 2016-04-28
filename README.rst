===============================
ceilometer-ecs
===============================

ECS Custom Meters for Ceilometer

This package provides files used by OpenStack Ceilometer to monitor the
usage meters of ECS stances. With this package installed
and configured, the Ceilometer Central Agent will poll remote ECS instances
via REST API, and store the results as meters with the name 'ecs.meter'.

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


OpenStack Configuration
-----------------------
