import os, sys
from datetime import datetime
import dateutil.parser
import iso8601
from ceilometer import sample
import ecs_mgmt_config
import ecs_mgmt_client

class ECSBillingDAO():
    def __init__(self, resource):
        config = ecs_mgmt_config.ECSManagementConfig(resource['ecs_ip'], resource['api_port'], resource['username'], resource['password'], resource['cert_path'])
        self.client = ecs_mgmt_client.ECSManagementClient(config)
        self.resource = resource

    def getSamples(self):
        samples = []
        self.client.login()
        namespaces = self.client.getNamespaces()
        self.client.logout()
        objs = 0
        sampletime = datetime(1970, 1, 1, tzinfo=iso8601.iso8601.UTC)
        for namespace in namespaces:
            objs += int(namespace['total_objects'])
            t = dateutil.parser.parse(namespace['sample_time'])
            if (sampletime < t): 
                sampletime = t
        s = sample.Sample(
            name='ecs.objects',
            type=sample.TYPE_GAUGE,
            unit='object',
            volume=objs,
            user_id=None,
            project_id=self.resource['project_id'],
            resource_id=self.resource['project_id'],
            timestamp=sampletime.isoformat(),
            resource_metadata=None
        ) 
        samples.append(s)

        return samples
