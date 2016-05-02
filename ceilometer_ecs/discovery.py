# -*- encoding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_config import cfg
from oslo_log import log

from ceilometer.compute import discovery
from ceilometer.i18n import _

LOG = log.getLogger(__name__)

cfg.CONF.register_group(cfg.OptGroup(
    name='ecs', title="Configuration for ECS Meters"
))

OPTS = [
    cfg.StrOpt('endpoint'),
    cfg.StrOpt('management_network'),
    cfg.BoolOpt('use_floating_ip', default=True)
]

cfg.CONF.register_opts(OPTS, group='ecs')


class ECSDiscovery(discovery.InstanceDiscovery):
    def __init__(self):
        super(ECSDiscovery, self).__init__()

    @property
    def management_network(self):
        return cfg.CONF['ecs'].management_network

    @property
    def use_floating(self):
        return cfg.CONF['ecs'].use_floating_ip

    def _instance_ip(self, instance):
        port = instance.addresses[self.management_network]

        # Only IPv4 for now
        use_ip = None
        for ip in port:
            if ip['version'] != 4:
                continue
            if self.use_floating and ip['OS-EXT-IPS:type'] != 'floating':
                continue
            use_ip = ip['addr']
            break

        # Treat no IP found the same as invalid network name
        if use_ip is None:
            raise KeyError

        return use_ip

    def discover(self, manager, param=None):
        instances = super(ECSDiscovery, self).discover(manager, param)
        endpoint = cfg.CONF['ecs'].endpoint

        resources = []
        resource = {
            'endpoint': endpoint
        }

        resources.append(resource)

        return resources
