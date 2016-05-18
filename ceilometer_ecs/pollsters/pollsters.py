#
# Copyright 2016 EMC Corp.
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
import abc

from oslo_log import log
from oslo_utils import timeutils
import six

from ceilometer.agent import plugin_base
from ceilometer import sample

from ceilometer_ecs import pollsters
from ceilometer_ecs.pollsters import ecs_billing_dao

LOG = log.getLogger(__name__)

@six.add_metaclass(abc.ABCMeta)
class ECSGaugePollster(pollsters.BaseECSPollster):

    def __init__(self):
        super(ECSGaugePollster, self).__init__()

    def get_samples(self, manager, cache, resources):
        samples = []
        for resource in resources:
            dao = ecs_billing_dao.ECSBillingDAO(resource)
            samples.extend(dao.getGaugeSamples())
        return samples

@six.add_metaclass(abc.ABCMeta)
class ECSDeltaPollster(pollsters.BaseECSPollster):

    def __init__(self):
        super(ECSDeltaPollster, self).__init__()

    def get_samples(self, manager, cache, resources):
        samples = []
        for resource in resources:
            dao = ecs_billing_dao.ECSBillingDAO(resource)
            samples.extend(dao.getDeltaSamples())
        return samples
