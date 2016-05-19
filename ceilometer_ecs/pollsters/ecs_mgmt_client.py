import os
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
        self.timezone = pytz.timezone(config.timezone)
        self.config = config

    def login(self):
        r = requests.get(self.base_url + '/login', auth=(self.config.username, self.config.password), verify=self.config.cert_path)
        self.headers = {self.AUTH_TOKEN: r.headers[self.AUTH_TOKEN]}

    def logout(self):
        r = requests.get(self.base_url + '/logout', headers=self.headers, verify=self.config.cert_path)

    def getVDCLocalID(self):
        r = requests.get(self.base_url + '/object/vdcs/vdc/local', headers=self.headers, verify=self.config.cert_path)
        root = ET.fromstring(r.text)
        return root.find('id').text

    def getNamespaces(self):
        now = datetime.now(self.timezone)
        if (self.config.frequency == 'Daily'):
            day = now.day
        else:
            day = 1
        endtime = self.timezone.localize(datetime(now.year, now.month, day, self.config.endhour))
        sampletime = self.timezone.localize(datetime(now.year, now.month, day, self.config.samplehour))

        namespaces = []
        nsdir = '/tmp/ceilometer-ecs'
        if not os.path.exists(nsdir):
            os.makedirs(nsdir)

        if (sampletime > now): # sampling should happen later
            return namespaces
        elif os.path.isfile(os.path.join(nsdir, endtime.isoformat())): # sampling already took place for this period
            return namespaces

        if(self.config.frequency == 'Daily'):
            starttime = endtime - timedelta(days=1) 
        else:
            year = endtime.year
            month = endtime.month
            if (month == 1):
                month = 12
                year -= 1
            else:
                month -= 1
            starttime  = self.timezone.localize(datetime(year, month, endtime.day, endtime.hour))
        endstr = endtime.astimezone(pytz.utc).isoformat()
        startstr = starttime.astimezone(pytz.utc).isoformat()
        f = open(os.path.join(nsdir, endtime.isoformat()), 'w')     

        r = requests.get(self.base_url + '/object/namespaces', headers=self.headers, verify=self.config.cert_path)
        root = ET.fromstring(r.text)
        f.write(r.text)

        for namespace in root.findall('namespace'):
            ns = {'id': namespace.find('id').text, 'name': namespace.find('name').text}
            r = requests.get(self.base_url + '/object/billing/namespace/' + ns['id'] + '/sample?sizeunit=KB&start_time=' + startstr + '&end_time=' + endstr, headers=self.headers, verify=self.config.cert_path)
            f.write(r.text)
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
            namespaces.append(ns)

        f.close()
        return namespaces
