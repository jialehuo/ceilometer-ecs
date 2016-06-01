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
import ecs_resource
from pollsters import ecs_billing_dao

LOG = log.getLogger(__name__)

cfg.CONF.register_group(cfg.OptGroup(
    name='ecs', title="Configuration for ECS Meters"
))

OPTS = [
    cfg.StrOpt('ecs_endpoint'),
    cfg.StrOpt('ecs_username'),
    cfg.StrOpt('ecs_password'),
    cfg.StrOpt('ecs_cert_path'),
    cfg.StrOpt('sample_start_time'),
    cfg.StrOpt('sample_interval'),
    cfg.StrOpt('sample_delay'),
    cfg.StrOpt('ceilometer_endpoint'),
    cfg.StrOpt('os_project_name'),
    cfg.StrOpt('os_projecct_domain_name'),
    cfg.StrOpt('os_username'),
    cfg.StrOpt('os_password'),
    cfg.StrOpt('os_user_domain_name'),
    cfg.StrOpt('os_auth_url')
]

cfg.CONF.register_opts(OPTS, group='ecs')

class ECSDiscovery(plugin_base.DiscoveryBase):
    def __init__(self):
        super(ECSDiscovery, self).__init__()

    def discover(self, manager, param=None):
        resources = [] 
  
        resource = ecs_resource.ECSResource(
            ecs_endpoint=cfg.CONF['ecs'].ecs_endpoint,
            ecs_username=cfg.CONF['ecs'].ecs_username,
            ecs_password=cfg.CONF['ecs'].ecs_password,
            ecs_cert_path=cfg.CONF['ecs'].ecs_cert_path,
            sample_start_time=dateutil.parser.parse(cfg.CONF['ecs'].sample_start_time),
            sample_interval=int(cfg.CONF['ecs'].sample_interval),
            sample_delay=int(cfg.CONF['ecs'].sample_delay),
            ceilometer_endpoint=cfg.CONF['ecs'].ceilometer_endpoint,
            os_project_name=cfg.CONF['ecs'].os_project_name,
            os_projecct_domain_name=cfg.CONF['ecs'].os_projecct_domain_name,
            os_username=cfg.CONF['ecs'].os_username,
            os_password=cfg.CONF['ecs'].os_password,
            os_user_domain_name=cfg.CONF['ecs'].os_user_domain_name,
            os_auth_url=cfg.CONF['ecs'].os_auth_url
        )
        dao = ecs_billing_dao.ECSBillingDAO(resource)
        resource.ecs_vdc_id = dao.getVDCLocalID()

        resources.append(resource)

        return resources        
