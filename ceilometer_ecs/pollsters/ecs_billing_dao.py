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

    def getGaugeSamples(self):
        samples = []
        self.client.login()
        namespaces = self.client.getNamespacesGauge()
        self.client.logout()
        objs = 0
        size = 0
        sampletime = datetime(1970, 1, 1, tzinfo=iso8601.iso8601.UTC)
        for namespace in namespaces:
            # add namespace gauge samples
            samples.append(self.getSample(
                name='ecs.namespaces.objects', 
                volume=namespace['total_objects'], 
                project_id=self.resource['project_id'], 
                resource_id=self.resource['vdc_id']+'/'+namespace['id'], 
                timestamp=namespace['sample_time'].isoformat())
            )
            samples.append(self.getSample(
                name='ecs.namespaces.objects.size', 
                unit='KB', 
                volume=namespace['total_size'], 
                project_id=self.resource['project_id'], 
                resource_id=self.resource['vdc_id']+'/'+namespace['id'], 
                timestamp=namespace['sample_time'].isoformat())
            )
            objs += namespace['total_objects']
            size += namespace['total_size']
            if (sampletime < namespace['sample_time']): 
                sampletime = namespace['sample_time']

        # add cluster gauge samples
        samples.append(self.getSample(
            name='ecs.objects', 
            volume=objs, 
            project_id=self.resource['project_id'],
            resource_id=self.resource['vdc_id'],
            timestamp=sampletime)
        )
        samples.append(self.getSample(
            name='ecs.objects.size',
            unit='KB',
            volume=size, 
            project_id=self.resource['project_id'],
            resource_id=self.resource['vdc_id'],
            timestamp=sampletime)
        )
        samples.append(self.getSample(
            name='ecs.objects.namespaces',
            unit='namespace',
            volume=len(namespaces), 
            project_id=self.resource['project_id'],
            resource_id=self.resource['vdc_id'],
            timestamp=sampletime)
        )

        return samples

    def getDeltaSamples(self):
        samples = []
        self.client.login()
        namespaces = self.client.getNamespacesDelta()
        self.client.logout()
        objs = 0
        size = 0
        sampletime = datetime(1970, 1, 1, tzinfo=iso8601.iso8601.UTC)
        for namespace in namespaces:
            # add namespace delta samples
            samples.append(self.getSample(
                name='ecs.namespaces.objects.delta', 
                type=sample.TYPE_DELTA, 
                volume=namespace['objects_delta'], 
                project_id=self.resource['project_id'], 
                resource_id=self.resource['vdc_id']+'/'+namespace['id'], 
                timestamp=namespace['sample_time'].isoformat())
            )
            samples.append(self.getSample(
                name='ecs.namespaces.objects.size.delta', 
                type=sample.TYPE_DELTA, 
                unit='B', 
                volume=namespace['bytes_delta'], 
                project_id=self.resource['project_id'], 
                resource_id=self.resource['vdc_id']+'/'+namespace['id'], 
                timestamp=namespace['sample_time'].isoformat())
            )
            objs += namespace['objects_delta']
            size += namespace['bytes_delta']
            if (sampletime < namespace['sample_time']): 
                sampletime = namespace['sample_time']

        # add cluster delta samples
        samples.append(self.getSample(
            name='ecs.objects.delta', 
            type=sample.TYPE_DELTA, 
            volume=objs, 
            project_id=self.resource['project_id'],
            resource_id=self.resource['vdc_id'],
            timestamp=sampletime)
        )
        samples.append(self.getSample(
            name='ecs.objects.size.delta',
            type=sample.TYPE_DELTA,
            unit='B',
            volume=size,
            project_id=self.resource['project_id'],
            resource_id=self.resource['vdc_id'],
            timestamp=sampletime)
        )

        return samples

    def getSample(self, name, volume, project_id, resource_id, timestamp, type=sample.TYPE_GAUGE, unit='object', user_id=None, resource_metadata=None):

        return sample.Sample(
            name=name,
            type=type,
            unit=unit,
            volume=volume,
            user_id=user_id,
            project_id=project_id,
            resource_id=resource_id,
            timestamp=timestamp,
            resource_metadata=resource_metadata
        )
