import re
from datetime import datetime, timedelta
import pytz
import requests
import xml.etree.ElementTree as ET
import dateutil.parser

class ECSManagementClient:

    AUTH_TOKEN = 'x-sds-auth-token'
    BUCKET_CREATED_PATTERN = re.compile('Bucket \\S+ has been created')
    BUCKET_DELETED_PATTERN = re.compile('Bucket \\S+ has been deleted')
    START_TIME_CACHE = 'ecs_start_time'

    def __init__(self, resource):
        self.base_url = 'https://' + resource.ecs_ip + ':' + resource.api_port
        self.resource = resource 

    def login(self):
        r = requests.get(self.base_url + '/login', auth=(self.resource.username, self.resource.password), verify=self.resource.cert_path)
        self.headers = {self.AUTH_TOKEN: r.headers[self.AUTH_TOKEN]}

    def logout(self):
        r = requests.get(self.base_url + '/logout', headers=self.headers, verify=self.resource.cert_path)

    def getVDCLocalID(self):
        r = requests.get(self.base_url + '/object/vdcs/vdc/local', headers=self.headers, verify=self.resource.cert_path)
        root = ET.fromstring(r.text)
        return root.find('id').text

    def isSampleTime(self, cache):
        if self.START_TIME_CACHE not in cache:
            cache[self.START_TIME_CACHE] = self.resource.start_time

        self.start_time = cache[self.START_TIME_CACHE]
        self.end_time = self.start_time + timedelta(minutes=self.resource.interval)
        self.sample_time = self.end_time + timedelta(minutes=self.resource.sample_delay)
        if (self.sample_time > datetime.now(pytz.utc)):
            return False
        else:
            return True

    def getNamespaceSamples(self, cache):
        namespaces = []
        if not self.isSampleTime(cache):
            return namespaces

        endstr = self.end_time.astimezone(pytz.utc).isoformat()
        startstr = self.start_time.astimezone(pytz.utc).isoformat()

        r = requests.get(self.base_url + '/object/namespaces', headers=self.headers, verify=self.resource.cert_path)
        root = ET.fromstring(r.text)

        for namespace in root.findall('namespace'):
            nsid = namespace.find('id').text
            ns = self.getNamespaceSample(nsid, startstr, endstr)
            namespaces.append(ns)

        cache[self.START_TIME_CACHE] = self.end_time
        return namespaces

    def getNamespaceSample(self, nsid, startstr, endstr):
        ns = {'id': nsid}

        r = requests.get(self.base_url + '/object/billing/namespace/' + nsid + '/sample?sizeunit=KB&include_bucket_detail=true&start_time=' + startstr + '&end_time=' + endstr, headers=self.headers, verify=self.resource.cert_path)
        root = ET.fromstring(r.text)
        ns['total_objects'] = long(root.find('total_objects').text)
        ns['total_buckets'] = len(root.findall('bucket_billing_sample'))
        ns['total_size'] = long(root.find('total_size').text)
        ns['total_size_unit'] = root.find('total_size_unit').text
        ns['objects_created'] = long(root.find('objects_created').text)
        ns['objects_deleted'] = long(root.find('objects_deleted').text)
        ns['bytes_delta'] = long(root.find('bytes_delta').text)
        ns['ingress'] = long(root.find('ingress').text)
        ns['egress'] = long(root.find('egress').text)
        ns['sample_start_time'] = dateutil.parser.parse(root.find('sample_start_time').text)
        ns['sample_end_time'] = dateutil.parser.parse(root.find('sample_end_time').text)

        # get bucket delta samples through audit events
        ns['buckets_created'] = 0
        ns['buckets_deleted'] = 0
        r = requests.get(self.base_url + '/vdc/events?namespace=' + nsid + '&start_time=' + startstr + '&end_time=' + endstr, headers=self.headers, verify=self.resource.cert_path)
        root = ET.fromstring(r.text)
        for auditevent in root.findall('./auditevent/description'):
            if self.BUCKET_CREATED_PATTERN.match(auditevent.text):
                ns['buckets_created'] += 1
            elif self.BUCKET_DELETED_PATTERN.match(auditevent.text):
                ns['buckets_deleted'] += 1 
        return ns
