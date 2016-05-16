import requests
import xml.etree.ElementTree as ET

class ECSManagementClient:
    AUTH_TOKEN = 'x-sds-auth-token'

    def __init__(self, config):
        self.base_url = 'https://' + config.ecs_ip + ':' + config.api_port
        self.username = config.username
        self.password = config.password
        self.cert_path = config.cert_path

    def login(self):
        r = requests.get(self.base_url + '/login', auth=(self.username, self.password), verify=self.cert_path)
        self.headers = {self.AUTH_TOKEN: r.headers[self.AUTH_TOKEN]}

    def getNamespaces(self):
        r = requests.get(self.base_url + '/object/namespaces', headers=self.headers, verify=self.cert_path)
        root = ET.fromstring(r.text)

        namespaces = []
        for namespace in root.findall('namespace'):
            ns = {'id': namespace.find('id').text, 'name': namespace.find('name').text}
            namespace.append(ns)
            r = requests.get(self.base_url + '/object/billing/namespace/' + ns['id'] + '/info?sizeunit=KB', headers=self.headers, verify=self.cert_path)
            bRoot = ET.fromstring(r.text)
            ns['total_size'] = bRoot.find('total_size').text
            ns['total_objects'] = bRoot.find('total_objects').text
            ns['sample_time'] = bRoot.find('sample_time').text
            # print ns
            namespaces.append(ns)
        return namespaces

    def logout(self):
        r = requests.get(self.base_url + '/logout', headers=self.headers, verify=self.cert_path)
