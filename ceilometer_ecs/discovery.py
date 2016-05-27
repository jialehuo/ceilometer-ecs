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

import dateutil.parser
from oslo_config import cfg
from oslo_log import log

from ceilometer.agent import plugin_base
from ceilometer.i18n import _
import ecs_instance
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
    cfg.StrOpt('start_time'),
    cfg.StrOpt('interval'),
    cfg.StrOpt('sample_delay')
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
        start_time = cfg.CONF['ecs'].start_time
        interval = cfg.CONF['ecs'].interval
        sample_delay = cfg.CONF['ecs'].sample_delay

        resources = [] 
  
        for tenant in manager.keystone.projects.list():
            if (project_name == tenant.name):
                resource = ecs_instance.ECSInstance(
                    ecs_ip=ecs_ip,
                    api_port=api_port,
                    username=username,
                    password=password,
                    cert_path=cert_path,
                    start_time=dateutil.parser.parse(start_time),
                    interval=int(interval),
                    sample_delay=int(sample_delay),
                    project_id=tenant.id
                )
                dao = ecs_billing_dao.ECSBillingDAO(resource)
                resource.vdc_id = dao.getVDCLocalID()

                resources.append(resource)

        return resources        
