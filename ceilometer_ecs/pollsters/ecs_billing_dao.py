import os, sys
from datetime import datetime
import iso8601
from ceilometer import sample
import ecs_mgmt_config
import ecs_mgmt_client

class ECSBillingDAO():
    def __init__(self, resource):
        config = ecs_mgmt_config.ECSManagementConfig(resource['ecs_ip'], resource['api_port'], resource['username'], resource['password'], resource['cert_path'], resource['timezone'], resource['frequency'], resource['end_hour'], resource['sample_hour'])
        self.client = ecs_mgmt_client.ECSManagementClient(config)
        self.resource = resource

    def getVDCLocalID(self):
        self.client.login()
        id = self.client.getVDCLocalID()
        self.client.logout()

        return id

    def getSamples(self):
        self.client.login()
        namespaces = self.client.getNamespaceSamples()
        self.client.logout()

        objs = 0
        size = 0
        objs_created = 0
        objs_deleted = 0
        bytes_delta = 0
        incoming_bytes = 0
        outgoing_bytes = 0
        sample_start_time = ''
        sample_end_time = ''
        samples = []

        for namespace in namespaces:
            sample_start_time = namespace['sample_start_time'].isoformat()
            sample_end_time = namespace['sample_end_time'].isoformat()

            # add namespace gauge samples
            samples.append(self.getSample(
                name='ecs.namespaces.objects', 
                volume=namespace['total_objects'], 
                project_id=self.resource['project_id'], 
                resource_id=self.resource['vdc_id']+'/'+namespace['id'], 
                timestamp=sample_end_time)
            )
            objs += namespace['total_objects']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.size', 
                unit=namespace['total_size_unit'], 
                volume=namespace['total_size'], 
                project_id=self.resource['project_id'], 
                resource_id=self.resource['vdc_id']+'/'+namespace['id'], 
                timestamp=sample_end_time)
            )
            size += namespace['total_size']

            # add namespace delta samples
            samples.append(self.getSample(
                name='ecs.namespaces.objects.created', 
                type=sample.TYPE_DELTA, 
                volume=namespace['objects_created'], 
                project_id=self.resource['project_id'], 
                resource_id=self.resource['vdc_id']+'/'+namespace['id'], 
                timestamp=sample_end_time,
                resource_metadata={'sample_start_time': sample_start_time,
                                   'sample_end_time': sample_end_time})
            )
            objs_created += namespace['objects_created']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.deleted', 
                type=sample.TYPE_DELTA, 
                volume=namespace['objects_deleted'], 
                project_id=self.resource['project_id'], 
                resource_id=self.resource['vdc_id']+'/'+namespace['id'], 
                timestamp=sample_end_time,
                resource_metadata={'sample_start_time': sample_start_time,
                                   'sample_end_time': sample_end_time})
            )
            objs_deleted += namespace['objects_deleted']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.bytes.delta', 
                type=sample.TYPE_DELTA, 
                unit='B', 
                volume=namespace['bytes_delta'], 
                project_id=self.resource['project_id'], 
                resource_id=self.resource['vdc_id']+'/'+namespace['id'], 
                timestamp=sample_end_time,
                resource_metadata={'sample_start_time': sample_start_time, 
                                   'sample_end_time': sample_end_time})
            )
            bytes_delta += namespace['bytes_delta']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.incoming.bytes', 
                type=sample.TYPE_DELTA, 
                unit='B', 
                volume=namespace['ingress'], 
                project_id=self.resource['project_id'], 
                resource_id=self.resource['vdc_id']+'/'+namespace['id'], 
                timestamp=sample_end_time,
                resource_metadata={'sample_start_time': sample_start_time,
                                   'sample_end_time': sample_end_time})
            )
            incoming_bytes += namespace['ingress']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.outgoing.bytes', 
                type=sample.TYPE_DELTA, 
                unit='B', 
                volume=namespace['egress'], 
                project_id=self.resource['project_id'], 
                resource_id=self.resource['vdc_id']+'/'+namespace['id'], 
                timestamp=sample_end_time,
                resource_metadata={'sample_start_time': sample_start_time,
                                   'sample_end_time': sample_end_time})
            )
            outgoing_bytes += namespace['egress']

        if (len(namespaces) > 0):
            # add cluster gauge samples
            samples.append(self.getSample(
                name='ecs.objects', 
                volume=objs, 
                project_id=self.resource['project_id'],
                resource_id=self.resource['vdc_id'],
                timestamp=sample_end_time)
            )
            samples.append(self.getSample(
                name='ecs.objects.size',
                unit=namespaces[0]['total_size_unit'],
                volume=size, 
                project_id=self.resource['project_id'],
                resource_id=self.resource['vdc_id'],
                timestamp=sample_end_time)
            )
            samples.append(self.getSample(
                name='ecs.objects.namespaces',
                unit='namespace',
                volume=len(namespaces), 
                project_id=self.resource['project_id'],
                resource_id=self.resource['vdc_id'],
                timestamp=sample_end_time)
            )

            # add cluster delta samples
            samples.append(self.getSample(
                name='ecs.objects.created', 
                type=sample.TYPE_DELTA, 
                volume=objs_created, 
                project_id=self.resource['project_id'],
                resource_id=self.resource['vdc_id'],
                timestamp=sample_end_time,
                resource_metadata={'sample_start_time': sample_start_time,
                                   'sample_end_time': sample_end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.deleted', 
                type=sample.TYPE_DELTA, 
                volume=objs_deleted, 
                project_id=self.resource['project_id'],
                resource_id=self.resource['vdc_id'],
                timestamp=sample_end_time,
                resource_metadata={'sample_start_time': sample_start_time,
                                   'sample_end_time': sample_end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.bytes.delta',
                type=sample.TYPE_DELTA,
                unit='B',
                volume=bytes_delta,
                project_id=self.resource['project_id'],
                resource_id=self.resource['vdc_id'],
                timestamp=sample_end_time,
                resource_metadata={'sample_start_time': sample_start_time,
                                   'sample_end_time': sample_end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.incoming.bytes',
                type=sample.TYPE_DELTA,
                unit='B',
                volume=incoming_bytes,
                project_id=self.resource['project_id'],
                resource_id=self.resource['vdc_id'],
                timestamp=sample_end_time,
                resource_metadata={'sample_start_time': sample_start_time,
                                   'sample_end_time': sample_end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.outgoing.bytes',
                type=sample.TYPE_DELTA,
                unit='B',
                volume=outgoing_bytes,
                project_id=self.resource['project_id'],
                resource_id=self.resource['vdc_id'],
                timestamp=sample_end_time,
                resource_metadata={'sample_start_time': sample_start_time,
                                   'sample_end_time': sample_end_time})
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
