import sys, os, shutil
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import ecs_resource
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pollsters'))
import ecs_billing_dao
import ecs_mgmt_client
import dateutil.parser
import requests
from ceilometerclient.v2 import client as ceiloclient

class Project:
    def __init__(self, id):
        self.id = id

proj1 = Project('jason')
proj2 = Project('proj2')

class Projects:
    def __init__(self, projects):
        self.projects = projects

    def list(self):
        return self.projects

class Keystone:
    def __init__(self, projects):
        self.projects = projects

class Manager:
    def __init__(self, keystone):
        self.keystone = keystone

resource = ecs_resource.ECSResource(
    ecs_endpoint='https://10.1.83.51:4443',
    ecs_username='jiale-huo-admin',
    ecs_password='dangerous',
    ecs_cert_path='/opt/stack/ecs-mgmt.cer',
    sample_start_time=dateutil.parser.parse('2016-05-24T12:00:00Z'),
    sample_interval=60,
    sample_delay=30,
    ceilometer_endpoint='http://127.0.0.1:8777',
    os_project_name='demo',
    os_project_domain_name='Default',
    os_username='admin',
    os_password='secret',
    os_user_domain_name='Default',
    os_auth_url='http://127.0.0.1/identity'
)

# client test
def testClient():
    client = ecs_mgmt_client.ECSManagementClient(resource)
    
    projs = [proj2]
    projects = Projects(projs)
    keystone = Keystone(projects)
    manager = Manager(keystone)

    client.login()
    print client.getNamespaceSamples(manager, {})
    projs.append(proj1)
    print client.getNamespaceSamples(manager, {})
    client.logout()

# DAO test
def testDAO():
    dao = ecs_billing_dao.ECSBillingDAO(resource)
    vdc_id = dao.getVDCLocalID()
    resource.vdc_id = vdc_id

    projs = [proj2]
    projects = Projects(projs)
    keystone = Keystone(projects)
    manager = Manager(keystone)
    print dao.getSamples(manager, {})

    projs.append(proj1)
    print dao.getSamples(manager, {})

def testAPI():
    kwargs = {
        'project_name': resource.os_project_name,
        'project_domain_name': resource.os_project_domain_name,
        'username': resource.os_username,
        'password': resource.os_password,
        'user_domain_name': resource.os_user_domain_name,
        'auth_url': resource.os_auth_url
    }

    client = ceiloclient.Client(resource.ceilometer_endpoint, **kwargs)
    query_samples = client.query_samples
    filter = "{\"=\": {\"meter\": \"ecs.objects\"}}"
    orderby = "[{\"timestamp\": \"DESC\"}]"
    limit = 1

    result = query_samples.query(filter=filter, orderby=orderby, limit=limit)
    print result[0].to_dict().get("metadata").get("sample_end_time")

testAPI()
testClient()
testDAO()
testAPI()
