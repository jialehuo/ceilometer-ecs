import abc

import six

from ceilometer.agent import plugin_base


@six.add_metaclass(abc.ABCMeta)
class BaseECSPollster(plugin_base.PollsterBase):

    def __init__(self):
        super(BaseECSPollster, self).__init__()


    @property
    def default_discovery(self):
        return 'ecs_instances'

