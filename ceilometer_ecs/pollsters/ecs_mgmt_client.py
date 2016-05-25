import os
import datetime
from datetime import datetime, timedelta
import pickle
import pytz
import requests
import xml.etree.ElementTree as ET
import dateutil.parser

class ECSManagementClient:

    AUTH_TOKEN = 'x-sds-auth-token'

    def __init__(self, config):
        self.base_url = 'https://' + config.ecs_ip + ':' + config.api_port
        self.config = config
        self.start_time_file = os.path.join(self.config.cache_dir, 'start-time')
        self.buckets_file = os.path.join(self.config.cache_dir, 'buckets')

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
        if os.path.exists(self.start_time_file):
            self.start_time = self.loadPickle(self.start_time_file)
        else:
            self.start_time = self.config.start_time
            self.prev_start_time = self.start_time - timedelta(minutes=self.config.interval)
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

        r = requests.get(self.base_url + '/object/namespaces', headers=self.headers, verify=self.config.cert_path)
        root = ET.fromstring(r.text)

        endstr = self.end_time.astimezone(pytz.utc).isoformat()
        startstr = self.start_time.astimezone(pytz.utc).isoformat()

        if os.path.exists(self.buckets_file):
            pbuckets = self.loadPickle(self.buckets_file)
        else:
            pbuckets = None
            pstartstr = self.prev_start_time.astimezone(pytz.utc).isoformat()
        buckets = {} 

        for namespace in root.findall('namespace'):
            nsid = namespace.find('id').text
            if pbuckets is None:
                prevns, pbucket = self.getNamespaceSample(nsid, pstartstr, startstr)
            else:
                pbucket = pbuckets[nsid]
            ns, bucket = self.getNamespaceSample(nsid, startstr, endstr)
            ns['buckets_created'] = len(bucket - pbucket)
            ns['buckets_deleted'] = len(pbucket - bucket)
            ns['total_buckets'] = len(bucket)
            buckets[nsid] = bucket
            namespaces.append(ns)

        if not os.path.exists(self.config.cache_dir):
            os.mkdir(self.config.cache_dir)
        self.dumpPickle(self.end_time, self.start_time_file)
        self.dumpPickle(buckets, self.buckets_file)
        return namespaces

    def dumpPickle(self, obj, filename):
        f = open(filename, 'w')
        pickle.dump(obj, f)
        f.close()

    def loadPickle(self, filename):
        f = open(filename, 'r')
        obj = pickle.load(f)
        f.close()
        return obj

    def getNamespaceSample(self, nsid, startstr, endstr):
        ns = {'id': nsid}

        r = requests.get(self.base_url + '/object/billing/namespace/' + nsid + '/sample?sizeunit=KB&include_bucket_detail=true&start_time=' + startstr + '&end_time=' + endstr, headers=self.headers, verify=self.config.cert_path)
        bRoot = ET.fromstring(r.text)
        ns['total_objects'] = long(bRoot.find('total_objects').text)
        ns['total_size'] = long(bRoot.find('total_size').text)
        ns['total_size_unit'] = bRoot.find('total_size_unit').text
        ns['objects_created'] = long(bRoot.find('objects_created').text)
        ns['objects_deleted'] = long(bRoot.find('objects_deleted').text)
        ns['bytes_delta'] = long(bRoot.find('bytes_delta').text)
        ns['ingress'] = long(bRoot.find('ingress').text)
        ns['egress'] = long(bRoot.find('egress').text)
        ns['sample_start_time'] = dateutil.parser.parse(bRoot.find('sample_start_time').text)
        ns['sample_end_time'] = dateutil.parser.parse(bRoot.find('sample_end_time').text)
        bucket = set()
        for b in bRoot.findall('bucket_billing_sample'):
            bucket.add(b.find('name').text)
        return ns, bucket
