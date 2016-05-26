import sys, os, shutil
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pollsters'))
import ecs_billing_dao
import ecs_mgmt_client
import ecs_mgmt_config
import dateutil.parser

# client test
def testClient():
    config = ecs_mgmt_config.ECSManagementConfig('10.1.83.51', '4443', 'jiale-huo-admin', 'dangerous', '/opt/stack/ecs-mgmt.cer', dateutil.parser.parse('2016-05-24T12:00:00Z'), 60, 30, '/opt/stack/ceilometer-ecs-cache')
    cache = {}
    client = ecs_mgmt_client.ECSManagementClient(config, cache)

    client.login()
    print client.getNamespaceSamples()
    print client.getNamespaceSamples()
    client.logout()

# DAO test
def testDAO():
    resource = {'ecs_ip': '10.1.83.51',
            'api_port': '4443',
            'username': 'jiale-huo-admin',
            'password': 'dangerous',
            'cert_path': '/opt/stack/ecs-mgmt.cer',
            'start_time': dateutil.parser.parse('2016-05-24T12:00:00Z'),
            'interval': 60,
            'sample_delay': 30,
            'cache_dir': '/opt/stack/ceilometer-ecs-cache',
            'project_id': '1234567890'}

    cache = {}
    dao = ecs_billing_dao.ECSBillingDAO(resource, cache)
    vdc_id = dao.getVDCLocalID()
    resource['vdc_id'] = vdc_id
    print dao.getSamples()
    print dao.getSamples()

# testClient()
testDAO()
