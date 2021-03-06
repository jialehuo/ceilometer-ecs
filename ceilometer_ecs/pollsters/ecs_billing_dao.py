from ceilometer import sample
import ecs_mgmt_client

class ECSBillingDAO():
    def __init__(self, resource):
        self.client = ecs_mgmt_client.ECSManagementClient(resource)
        self.resource = resource

    def getVDCLocalID(self):
        self.client.login()
        id = self.client.getVDCLocalID()
        self.client.logout()

        return id

    def getSamples(self, manager, cache):
        self.client.login()
        namespaces = self.client.getNamespaceSamples(manager, cache)
        self.client.logout()

        samples = []

        objs = 0
        buckets = 0
        size = 0
        objs_created = 0
        objs_deleted = 0
        buckets_created = 0
        buckets_deleted = 0
        bytes_delta = 0
        incoming_bytes = 0
        outgoing_bytes = 0
        start_time = cache.get(self.client.START_TIME_CACHE)
        end_time = cache.get(self.client.END_TIME_CACHE)
        timestamp = cache.get(self.client.TIMESTAMP_CACHE)

        for namespace in namespaces:
            # add namespace gauge samples
            samples.append(self.getSample(
                name='ecs.namespaces.objects', 
                volume=namespace['total_objects'], 
                project_id=namespace['id'], 
                resource_id=self.resource.ecs_vdc_id+'/'+namespace['id'], 
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
             )
            objs += namespace['total_objects']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.buckets',
                unit='bucket',
                volume=namespace['total_buckets'], 
                project_id=namespace['id'], 
                resource_id=self.resource.ecs_vdc_id+'/'+namespace['id'], 
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
             )
            buckets += namespace['total_buckets']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.size', 
                unit=namespace['total_size_unit'], 
                volume=namespace['total_size'], 
                project_id=namespace['id'], 
                resource_id=self.resource.ecs_vdc_id+'/'+namespace['id'], 
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
             )
            size += namespace['total_size']

            # add namespace delta samples
            samples.append(self.getSample(
                name='ecs.namespaces.objects.created', 
                type=sample.TYPE_DELTA, 
                volume=namespace['objects_created'], 
                project_id=namespace['id'], 
                resource_id=self.resource.ecs_vdc_id+'/'+namespace['id'], 
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            objs_created += namespace['objects_created']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.deleted', 
                type=sample.TYPE_DELTA, 
                volume=namespace['objects_deleted'], 
                project_id=namespace['id'], 
                resource_id=self.resource.ecs_vdc_id+'/'+namespace['id'], 
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            objs_deleted += namespace['objects_deleted']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.buckets.created', 
                type=sample.TYPE_DELTA,
                unit='bucket',
                volume=namespace['buckets_created'], 
                project_id=namespace['id'], 
                resource_id=self.resource.ecs_vdc_id+'/'+namespace['id'], 
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            buckets_created += namespace['buckets_created']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.buckets.deleted', 
                type=sample.TYPE_DELTA,
                unit='bucket',
                volume=namespace['buckets_deleted'], 
                project_id=namespace['id'], 
                resource_id=self.resource.ecs_vdc_id+'/'+namespace['id'], 
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            buckets_deleted += namespace['buckets_deleted']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.bytes.delta', 
                type=sample.TYPE_DELTA, 
                unit='B', 
                volume=namespace['bytes_delta'], 
                project_id=namespace['id'], 
                resource_id=self.resource.ecs_vdc_id+'/'+namespace['id'], 
                timestamp=timestamp,
                resource_metadata={'start_time': start_time, 
                                   'end_time': end_time})
            )
            bytes_delta += namespace['bytes_delta']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.incoming.bytes', 
                type=sample.TYPE_DELTA, 
                unit='B', 
                volume=namespace['ingress'], 
                project_id=namespace['id'], 
                resource_id=self.resource.ecs_vdc_id+'/'+namespace['id'], 
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            incoming_bytes += namespace['ingress']

            samples.append(self.getSample(
                name='ecs.namespaces.objects.outgoing.bytes', 
                type=sample.TYPE_DELTA, 
                unit='B', 
                volume=namespace['egress'], 
                project_id=namespace['id'], 
                resource_id=self.resource.ecs_vdc_id+'/'+namespace['id'], 
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            outgoing_bytes += namespace['egress']

        agg_proj_id = None    # aggregated meters project ID

        if (len(namespaces) > 0):
            # add cluster gauge samples
            samples.append(self.getSample(
                name='ecs.objects', 
                volume=objs, 
                project_id=agg_proj_id,
                resource_id=self.resource.ecs_vdc_id,
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.buckets',
                unit='bucket',
                volume=buckets, 
                project_id=agg_proj_id,
                resource_id=self.resource.ecs_vdc_id,
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.size',
                unit=namespaces[0]['total_size_unit'],
                volume=size, 
                project_id=agg_proj_id,
                resource_id=self.resource.ecs_vdc_id,
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.namespaces',
                unit='namespace',
                volume=len(namespaces), 
                project_id=agg_proj_id,
                resource_id=self.resource.ecs_vdc_id,
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )

            # add cluster delta samples
            samples.append(self.getSample(
                name='ecs.objects.created', 
                type=sample.TYPE_DELTA, 
                volume=objs_created, 
                project_id=agg_proj_id,
                resource_id=self.resource.ecs_vdc_id,
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.deleted', 
                type=sample.TYPE_DELTA, 
                volume=objs_deleted, 
                project_id=agg_proj_id,
                resource_id=self.resource.ecs_vdc_id,
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.buckets.created', 
                type=sample.TYPE_DELTA,
                unit='bucket',
                volume=buckets_created, 
                project_id=agg_proj_id,
                resource_id=self.resource.ecs_vdc_id,
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.buckets.deleted', 
                type=sample.TYPE_DELTA,
                unit='bucket', 
                volume=buckets_deleted, 
                project_id=agg_proj_id,
                resource_id=self.resource.ecs_vdc_id,
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.bytes.delta',
                type=sample.TYPE_DELTA,
                unit='B',
                volume=bytes_delta,
                project_id=agg_proj_id,
                resource_id=self.resource.ecs_vdc_id,
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.incoming.bytes',
                type=sample.TYPE_DELTA,
                unit='B',
                volume=incoming_bytes,
                project_id=agg_proj_id,
                resource_id=self.resource.ecs_vdc_id,
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
            )
            samples.append(self.getSample(
                name='ecs.objects.outgoing.bytes',
                type=sample.TYPE_DELTA,
                unit='B',
                volume=outgoing_bytes,
                project_id=agg_proj_id,
                resource_id=self.resource.ecs_vdc_id,
                timestamp=timestamp,
                resource_metadata={'start_time': start_time,
                                   'end_time': end_time})
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
