import abc

from oslo_log import log
import six

from ceilometer_ecs import pollsters
from ceilometer_ecs.pollsters import ecs_billing_dao

LOG = log.getLogger(__name__)

@six.add_metaclass(abc.ABCMeta)
class ECSBillingPollster(pollsters.BaseECSPollster):

    def __init__(self):
        super(ECSBillingPollster, self).__init__()

    def get_samples(self, manager, cache, resources):
        samples = []
        for resource in resources:
            dao = ecs_billing_dao.ECSBillingDAO(resource)
            samples.extend(dao.getSamples(manager, cache))
        return samples

