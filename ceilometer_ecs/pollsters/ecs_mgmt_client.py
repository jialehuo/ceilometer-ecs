import re
from datetime import datetime, timedelta
import pytz
import requests
import xml.etree.ElementTree as ET
import dateutil.parser
from ceilometerclient.v2 import client as ceiloclient

class ECSManagementClient:

    AUTH_TOKEN = 'x-sds-auth-token'
    BUCKET_CREATED_PATTERN = re.compile('Bucket \\S+ has been created')
    BUCKET_DELETED_PATTERN = re.compile('Bucket \\S+ has been deleted')
    START_TIME_CACHE = 'ecs_start_time'

    def __init__(self, resource):
        self.resource = resource 

    def isValidElem(self, elem):
        return (elem is not None) and (elem.text is not None) and bool(elem.text.strip())

    def login(self):
        r = requests.get(self.resource.ecs_endpoint + '/login', auth=(self.resource.ecs_username, self.resource.ecs_password), verify=self.resource.ecs_cert_path)
        self.headers = {self.AUTH_TOKEN: r.headers[self.AUTH_TOKEN]}

    def logout(self):
        r = requests.get(self.resource.ecs_endpoint + '/logout', headers=self.headers, verify=self.resource.ecs_cert_path)

    def getVDCLocalID(self):
        r = requests.get(self.resource.ecs_endpoint + '/object/vdcs/vdc/local', headers=self.headers, verify=self.resource.ecs_cert_path)
        root = ET.fromstring(r.text)
        if self.isValidElem(root.find('id')):
            return root.find('id').text.strip()
        else:
            return None

    def getStartTime(self):
        kwargs = {
            'project_name': self.resource.os_project_name, 
            'project_domain_name': self.resource.os_project_domain_name, 
            'username': self.resource.os_username, 
            'password': self.resource.os_password, 
            'user_domain_name': self.resource.os_user_domain_name, 
            'auth_url': self.resource.os_auth_url
        }
 
        client = ceiloclient.Client(self.resource.ceilometer_endpoint, **kwargs)
        filter = "{\"=\": {\"meter\": \"ecs.objects\"}}"
        orderby = "[{\"timestamp\": \"DESC\"}]"
        limit = 1

        result = client.query_samples.query(filter=filter, orderby=orderby, limit=limit)
        if (result is not None) and (len(result) > 0) and (result[0].to_dict() is not None) and (result[0].to_dict().get("metadata") is not None) and (result[0].to_dict().get("metadata").get("sample_end_time") is not None):
            return dateutil.parser.parse(result[0].to_dict().get("metadata").get("sample_end_time"))
        else:
            return self.resource.sample_start_time

    def isSampleTime(self, cache):
        if self.START_TIME_CACHE not in cache:
            cache[self.START_TIME_CACHE] = self.getStartTime()

        self.start_time = cache[self.START_TIME_CACHE]
        self.end_time = self.start_time + timedelta(minutes=self.resource.sample_interval)
        self.sample_time = self.end_time + timedelta(minutes=self.resource.sample_delay)
        if (self.sample_time > datetime.now(pytz.utc)):
            return False
        else:
            return True

    def getNamespaceSamples(self, manager, cache):
        namespaces = []
        if not self.isSampleTime(cache):
            return namespaces

        endstr = self.end_time.astimezone(pytz.utc).isoformat()
        startstr = self.start_time.astimezone(pytz.utc).isoformat()

        if manager.keystone.version == 'v3':
            projects = manager.keystone.projects.list()
        else:
            projects = manager.keystone.tenants.list()

        for project in projects:
            namespace = self.getNamespaceSample(project.id, startstr, endstr)
            if namespace is not None:
                namespaces.append(namespace)

        cache[self.START_TIME_CACHE] = self.end_time

        return namespaces

    def getNamespaceSample(self, id, startstr, endstr):
        namespace = {'id': id, 'total_buckets': 0}
        next_marker = ''

        while True:
            r = requests.get(self.resource.ecs_endpoint + '/object/billing/namespace/' + id + '/sample?sizeunit=KB&include_bucket_detail=true&start_time=' + startstr + '&end_time=' + endstr + next_marker, headers=self.headers, verify=self.resource.ecs_cert_path)
            root = ET.fromstring(r.text)

            if root.tag == 'error':
                return None

            if self.isValidElem(root.find('total_objects')):
                namespace['total_objects'] = long(root.find('total_objects').text.strip())
            if self.isValidElem(root.find('total_size')):
                namespace['total_size'] = long(root.find('total_size').text.strip())
            if self.isValidElem(root.find('total_size_unit')):
                namespace['total_size_unit'] = root.find('total_size_unit').text.strip()
            if self.isValidElem(root.find('objects_created')):
                namespace['objects_created'] = long(root.find('objects_created').text.strip())
            if self.isValidElem(root.find('objects_deleted')):
                namespace['objects_deleted'] = long(root.find('objects_deleted').text.strip())
            if self.isValidElem(root.find('bytes_delta')):
                namespace['bytes_delta'] = long(root.find('bytes_delta').text.strip())
            if self.isValidElem(root.find('ingress')):
                namespace['ingress'] = long(root.find('ingress').text.strip())
            if self.isValidElem(root.find('egress')):
                namespace['egress'] = long(root.find('egress').text.strip())
            if self.isValidElem(root.find('sample_start_time')):
                namespace['sample_start_time'] = dateutil.parser.parse(root.find('sample_start_time').text.strip())
            if self.isValidElem(root.find('sample_end_time')):
                namespace['sample_end_time'] = dateutil.parser.parse(root.find('sample_end_time').text.strip())
            if (root.findall('./bucket_billing_sample/name') is not None):
                namespace['total_buckets'] += len(root.findall('./bucket_billing_sample/name'))
            
            if self.isValidElem(root.find('next_marker')):
                next_marker = '&marker=' + root.find('next_marker').text.strip()
            else:
                break

        # get bucket delta samples through audit events
        namespace['buckets_created'] = 0
        namespace['buckets_deleted'] = 0
        next_marker = ''
        while True:
            r = requests.get(self.resource.ecs_endpoint + '/vdc/events?namespace=' + id + '&start_time=' + startstr + '&end_time=' + endstr + next_marker, headers=self.headers, verify=self.resource.ecs_cert_path)
            root = ET.fromstring(r.text)
            for auditevent in root.findall('./auditevent/description'):
                if self.BUCKET_CREATED_PATTERN.match(auditevent.text):
                    namespace['buckets_created'] += 1
                elif self.BUCKET_DELETED_PATTERN.match(auditevent.text):
                    namespace['buckets_deleted'] += 1
            if self.isValidElem(root.find('NextMarker')):
                next_marker = '&marker=' + root.find('NextMarker').text.strip()
            else:
                break

        return namespace
