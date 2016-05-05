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

from oslo_utils import timeutils
import six

from ceilometer.agent import plugin_base
from ceilometer import sample


@six.add_metaclass(abc.ABCMeta)
class BaseECSPollster(plugin_base.PollsterBase):

    def __init__(self):
        super(BaseECSPollster, self).__init__()


    @property
    def default_discovery(self):
        return 'tenant'

    def get_samples(self, manager, cache, resources):
        samples = []
        for tenant in resources:
            s = sample.Sample(
                name='ecs.objects',
                type=sample.TYPE_GAUGE,
                unit='object',
                volume=1,
                user_id=None,
                project_id=tenant.id,
                resource_id=tenant.id,
                timestamp=timeutils.utcnow().isoformat(),
                resource_metadata=None,
            )
            samples.append(s)
        return samples
