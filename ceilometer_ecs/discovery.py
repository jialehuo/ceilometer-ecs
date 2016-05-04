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

from ceilometer.agent import plugin_base
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


class ECSDiscovery(plugin_base.DiscoveryBase):
    def __init__(self):
        super(ECSDiscovery, self).__init__()

    def discover(self, manager, param=None):
        endpoint = cfg.CONF['ecs'].endpoint

        resources = []
        resource = {
            'endpoint': endpoint,
            'project_id': '1234567890',
            'resource_id': '1234567890'
        }

        resources.append(resource)

        return resources
