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
from pollsters import ecs_billing_dao

LOG = log.getLogger(__name__)

cfg.CONF.register_group(cfg.OptGroup(
    name='ecs', title="Configuration for ECS Meters"
))

OPTS = [
    cfg.StrOpt('project_name'),
    cfg.StrOpt('ecs_ip'),
    cfg.StrOpt('api_port'),
    cfg.StrOpt('username'),
    cfg.StrOpt('password'),
    cfg.StrOpt('cert_path'),
    cfg.StrOpt('timezone'),
    cfg.StrOpt('frequency'),
    cfg.StrOpt('end_hour'),
    cfg.StrOpt('sample_hour')
]

cfg.CONF.register_opts(OPTS, group='ecs')


class ECSDiscovery(plugin_base.DiscoveryBase):
    def __init__(self):
        super(ECSDiscovery, self).__init__()

    def discover(self, manager, param=None):
        project_name = cfg.CONF['ecs'].project_name
        ecs_ip = cfg.CONF['ecs'].ecs_ip
        api_port = cfg.CONF['ecs'].api_port
        username = cfg.CONF['ecs'].username
        password = cfg.CONF['ecs'].password
        cert_path = cfg.CONF['ecs'].cert_path
        timezone = cfg.CONF['ecs'].timezone
        frequency = cfg.CONF['ecs'].frequency
        end_hour = cfg.CONF['ecs'].end_hour
        sample_hour = cfg.CONF['ecs'].sample_hour

        resources = [] 
  
        for tenant in manager.keystone.projects.list():
            if (project_name == tenant.name):
                resource = {
                    'project_id': tenant.id,
                    'ecs_ip': ecs_ip,
                    'api_port': api_port,
                    'username': username,
                    'password': password,
                    'cert_path': cert_path,
                    'timezone': timezone,
                    'frequency': frequency,
                    'end_hour': int(end_hour),
                    'sample_hour': int(sample_hour)
                }
                dao = ecs_billing_dao.ECSBillingDAO(resource)
                resource['vdc_id'] = dao.getVDCLocalID()

                resources.append(resource)

        return resources        
