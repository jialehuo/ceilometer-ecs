import os, sys
from datetime import datetime
import iso8601
from ceilometer import sample
import ecs_mgmt_config
import ecs_mgmt_client

class ECSBillingDAO():
    def __init__(self, resource):
        config = ecs_mgmt_config.ECSManagementConfig(resource['ecs_ip'], resource['api_port'], resource['username'], resource['password'], resource['cert_path'])
        self.client = ecs_mgmt_client.ECSManagementClient(config)
        self.resource = resource

    def getVDCLocalID(self):
        self.client.login()
        id = self.client.getVDCLocalID()
        self.client.logout()

        return id

    def getSamples(self):
        samples = []
        self.client.login()
        namespaces = self.client.getNamespaces()
        self.client.logout()
        objs = 0
        size = 0
        sampletime = datetime(1970, 1, 1, tzinfo=iso8601.iso8601.UTC)
        for namespace in namespaces:
            samples.append(self.getNamespacesObjectsSample(namespace))
            samples.append(self.getNamespacesSizeSample(namespace))
            objs += namespace['total_objects']
            size += namespace['total_size']
            if (sampletime < namespace['sample_time']): 
                sampletime = namespace['sample_time']

        samples.append(self.getObjectsSample(objs, sampletime))
        samples.append(self.getSizeSample(size, sampletime))
        samples.append(self.getNamespacesSample(namespaces, sampletime))

        return samples

    def getObjectsSample(self, objs, sampletime):

        return sample.Sample(
            name='ecs.objects',
            type=sample.TYPE_GAUGE,
            unit='object',
            volume=objs,
            user_id=None,
            project_id=self.resource['project_id'],
            resource_id=self.resource['vdc_id'],
            timestamp=sampletime.isoformat(),
            resource_metadata=None
        ) 

    def getSizeSample(self, size, sampletime):

        return sample.Sample(
            name='ecs.objects.size',
            type=sample.TYPE_GAUGE,
            unit='KB',
            volume=size,
            user_id=None,
            project_id=self.resource['project_id'],
            resource_id=self.resource['vdc_id'],
            timestamp=sampletime.isoformat(),
            resource_metadata=None
        )

    def getNamespacesSample(self, namespaces, sampletime):

        return sample.Sample(
            name='ecs.objects.namespaces',
            type=sample.TYPE_GAUGE,
            unit='namespace',
            volume=len(namespaces),
            user_id=None,
            project_id=self.resource['project_id'],
            resource_id=self.resource['vdc_id'],
            timestamp=sampletime.isoformat(),
            resource_metadata=None
        )

    def getNamespacesObjectsSample(self, namespace):

        return sample.Sample(
            name='ecs.namespaces.objects',
            type=sample.TYPE_GAUGE,
            unit='object',
            volume=namespace['total_objects'],
            user_id=None,
            project_id=self.resource['project_id'],
            resource_id=self.resource['vdc_id'] + '/' + namespace['id'],
            timestamp=namespace['sample_time'].isoformat(),
            resource_metadata=None
        )
 
    def getNamespacesSizeSample(self, namespace):

        return sample.Sample(
            name='ecs.namespaces.objects.size',
            type=sample.TYPE_GAUGE,
            unit='KB',
            volume=namespace['total_size'],
            user_id=None,
            project_id=self.resource['project_id'],
            resource_id=self.resource['vdc_id'] + '/' + namespace['id'],
            timestamp=namespace['sample_time'].isoformat(),
            resource_metadata=None
        )
