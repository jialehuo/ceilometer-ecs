import datetime
from datetime import datetime, timedelta
import pytz
import requests
import xml.etree.ElementTree as ET
import dateutil.parser

class ECSManagementClient:
    AUTH_TOKEN = 'x-sds-auth-token'

    def __init__(self, config):
        self.base_url = 'https://' + config.ecs_ip + ':' + config.api_port
        self.username = config.username
        self.password = config.password
        self.cert_path = config.cert_path
        self.timezone = pytz.timezone(config.timezone)
        self.frequency = config.frequency

    def login(self):
        r = requests.get(self.base_url + '/login', auth=(self.username, self.password), verify=self.cert_path)
        self.headers = {self.AUTH_TOKEN: r.headers[self.AUTH_TOKEN]}

    def logout(self):
        r = requests.get(self.base_url + '/logout', headers=self.headers, verify=self.cert_path)

    def getVDCLocalID(self):
        r = requests.get(self.base_url + '/object/vdcs/vdc/local', headers=self.headers, verify=self.cert_path)
        root = ET.fromstring(r.text)
        return root.find('id').text

    def getNamespacesGauge(self):
        r = requests.get(self.base_url + '/object/namespaces', headers=self.headers, verify=self.cert_path)
        root = ET.fromstring(r.text)

        namespaces = []
        for namespace in root.findall('namespace'):
            ns = {'id': namespace.find('id').text, 'name': namespace.find('name').text}
            r = requests.get(self.base_url + '/object/billing/namespace/' + ns['id'] + '/info?sizeunit=KB', headers=self.headers, verify=self.cert_path)
            bRoot = ET.fromstring(r.text)
            ns['total_size'] = long(bRoot.find('total_size').text)
            ns['total_objects'] = long(bRoot.find('total_objects').text)
            ns['sample_time'] = dateutil.parser.parse(bRoot.find('sample_time').text)
            namespaces.append(ns)
        return namespaces

    def getNamespacesDelta(self):
        r = requests.get(self.base_url + '/object/namespaces', headers=self.headers, verify=self.cert_path)
        root = ET.fromstring(r.text)

        now = datetime.now(self.timezone)
        if (self.frequency == 'Daily'):
            day = now.day
        else:
            day = 1
        endtime = datetime(now.year, now.month, day)
        if (self.frequency == 'Daily'):
            starttime = endtime - timedelta(days=1) 
        else:
            starttime  = endtime - timedelta(months=1)
        endstr = self.timezone.localize(endtime).isoformat()
        startstr = self.timezone.localize(starttime).isoformat()

        namespaces = []
        for namespace in root.findall('namespace'):
            ns = {'id': namespace.find('id').text, 'name': namespace.find('name').text}
            r = requests.get(self.base_url + '/object/billing/namespace/' + ns['id'] + '/sample?sizeunit=KB&start_time=' + startstr + '&end_time=' + endstr, headers=self.headers, verify=self.cert_path)
            bRoot = ET.fromstring(r.text)
            ns['bytes_delta'] = long(bRoot.find('bytes_delta').text)
            ns['objects_delta'] = long(bRoot.find('objects_created').text) - long(bRoot.find('objects_deleted').text)
            ns['sample_time'] = dateutil.parser.parse(bRoot.find('sample_end_time').text)
            namespaces.append(ns)
        return namespaces
