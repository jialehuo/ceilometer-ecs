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
from ceilometer.agent.discovery import tenant

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


class ECSDiscovery(tenant.TenantDiscovery):
    def __init__(self):
        super(ECSDiscovery, self).__init__()

    def discover(self, manager, param=None):
        endpoint = cfg.CONF['ecs'].endpoint

        return super(ECSDiscovery, manager, param=None)
