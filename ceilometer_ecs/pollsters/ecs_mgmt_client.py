import os
import re
import datetime
from datetime import datetime, timedelta
import pickle
import pytz
import requests
import xml.etree.ElementTree as ET
import dateutil.parser

class ECSManagementClient:

    AUTH_TOKEN = 'x-sds-auth-token'
    BUCKET_CREATED_PATTERN = re.compile('Bucket \\S+ has been created')
    BUCKET_DELETED_PATTERN = re.compile('Bucket \\S+ has been deleted')
    START_TIME_CACHE = 'ecs_start_time'

    def __init__(self, config, cache):
        self.base_url = 'https://' + config.ecs_ip + ':' + config.api_port
        self.config = config
        self.cache = cache

    def login(self):
        r = requests.get(self.base_url + '/login', auth=(self.config.username, self.config.password), verify=self.config.cert_path)
        self.headers = {self.AUTH_TOKEN: r.headers[self.AUTH_TOKEN]}

    def logout(self):
        r = requests.get(self.base_url + '/logout', headers=self.headers, verify=self.config.cert_path)

    def getVDCLocalID(self):
        r = requests.get(self.base_url + '/object/vdcs/vdc/local', headers=self.headers, verify=self.config.cert_path)
        root = ET.fromstring(r.text)
        return root.find('id').text

    def isSampleTime(self):
        if self.START_TIME_CACHE not in self.cache:
            self.cache[self.START_TIME_CACHE] = self.config.start_time

        self.start_time = self.cache[self.START_TIME_CACHE]
        self.end_time = self.start_time + timedelta(minutes=self.config.interval)
        self.sample_time = self.end_time + timedelta(minutes=self.config.sample_delay)
        if (self.sample_time > datetime.now(pytz.utc)):
            return False
        else:
            return True

    def getNamespaceSamples(self):
        namespaces = []
        if not self.isSampleTime():
            return namespaces

        endstr = self.end_time.astimezone(pytz.utc).isoformat()
        startstr = self.start_time.astimezone(pytz.utc).isoformat()

        r = requests.get(self.base_url + '/object/namespaces', headers=self.headers, verify=self.config.cert_path)
        root = ET.fromstring(r.text)

        for namespace in root.findall('namespace'):
            nsid = namespace.find('id').text
            ns = self.getNamespaceSample(nsid, startstr, endstr)
            namespaces.append(ns)

        self.cache[self.START_TIME_CACHE] = self.end_time
        return namespaces

    def getNamespaceSample(self, nsid, startstr, endstr):
        ns = {'id': nsid}

        r = requests.get(self.base_url + '/object/billing/namespace/' + nsid + '/sample?sizeunit=KB&include_bucket_detail=true&start_time=' + startstr + '&end_time=' + endstr, headers=self.headers, verify=self.config.cert_path)
        bRoot = ET.fromstring(r.text)
        ns['total_objects'] = long(bRoot.find('total_objects').text)
        ns['total_buckets'] = len(bRoot.findall('bucket_billing_sample'))
        ns['total_size'] = long(bRoot.find('total_size').text)
        ns['total_size_unit'] = bRoot.find('total_size_unit').text
        ns['objects_created'] = long(bRoot.find('objects_created').text)
        ns['objects_deleted'] = long(bRoot.find('objects_deleted').text)
        ns['bytes_delta'] = long(bRoot.find('bytes_delta').text)
        ns['ingress'] = long(bRoot.find('ingress').text)
        ns['egress'] = long(bRoot.find('egress').text)
        ns['sample_start_time'] = dateutil.parser.parse(bRoot.find('sample_start_time').text)
        ns['sample_end_time'] = dateutil.parser.parse(bRoot.find('sample_end_time').text)

        # get bucket delta samples through audit events
        ns['buckets_created'] = 0
        ns['buckets_deleted'] = 0
        r = requests.get(self.base_url + '/vdc/events?namespace=' + nsid + '&start_time=' + startstr + '&end_time=' + endstr, headers=self.headers, verify=self.config.cert_path)
        bRoot = ET.fromstring(r.text)
        for auditevent in bRoot.findall('./auditevent/description'):
            if self.BUCKET_CREATED_PATTERN.match(auditevent.text):
                ns['buckets_created'] += 1
            elif self.BUCKET_DELETED_PATTERN.match(auditevent.text):
                ns['buckets_deleted'] += 1 
        return ns
