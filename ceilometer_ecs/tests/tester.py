import sys, os, shutil
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import ecs_instance
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pollsters'))
import ecs_billing_dao
import ecs_mgmt_client
import dateutil.parser

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

resource = ecs_instance.ECSInstance(
    ecs_ip='10.1.83.51',
    api_port='4443',
    username='jiale-huo-admin',
    password='dangerous',
    cert_path='/opt/stack/ecs-mgmt.cer',
    start_time=dateutil.parser.parse('2016-05-24T12:00:00Z'),
    interval=60,
    sample_delay=30
)
cache = {}

# client test
def testClient():
    client = ecs_mgmt_client.ECSManagementClient(resource)
    
    projs = [proj2]
    projects = Projects(projs)
    keystone = Keystone(projects)
    manager = Manager(keystone)

    client.login()
    print client.getNamespaceSamples(manager, cache)
    projs.append(proj1)
    print client.getNamespaceSamples(manager, cache)
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
    print dao.getSamples(manager, cache)

    projs.append(proj1)
    print dao.getSamples(manager, cache)

testClient()
testDAO()
