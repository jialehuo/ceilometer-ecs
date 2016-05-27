import sys, os, shutil
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import ecs_instance
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pollsters'))
import ecs_billing_dao
import ecs_mgmt_client
import dateutil.parser

resource = ecs_instance.ECSInstance(
    ecs_ip='10.1.83.51',
    api_port='4443',
    username='jiale-huo-admin',
    password='dangerous',
    cert_path='/opt/stack/ecs-mgmt.cer',
    start_time=dateutil.parser.parse('2016-05-24T12:00:00Z'),
    interval=60,
    sample_delay=30,
    project_id='1234567890'
)
cache = {}

def testDashboard():
    client = ecs_mgmt_client.ECSManagementClient(resource)

    client.login()
    client.getDashboard()
    client.logout()

# client test
def testClient():
    client = ecs_mgmt_client.ECSManagementClient(resource)

    client.login()
    print client.getNamespaceSamples(cache)
    print client.getNamespaceSamples(cache)
    client.logout()

# DAO test
def testDAO():
    dao = ecs_billing_dao.ECSBillingDAO(resource)
    vdc_id = dao.getVDCLocalID()
    resource.vdc_id = vdc_id
    print dao.getSamples(cache)
    print dao.getSamples(cache)

testDashboard()
# testClient()
# testDAO()
