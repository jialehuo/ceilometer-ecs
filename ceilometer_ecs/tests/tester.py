import sys, os, shutil
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pollsters'))
import ecs_billing_dao
import ecs_mgmt_client
import ecs_mgmt_config

# cleanup
def cleanup():
    shutil.rmtree('/tmp/ceilometer-ecs')

# client test
def testClient():
    config = ecs_mgmt_config.ECSManagementConfig('10.1.83.51', '4443', 'jiale-huo-admin', 'dangerous', '/opt/stack/ecs-mgmt.cer', 'Asia/Shanghai', 'Hourly')
    client = ecs_mgmt_client.ECSManagementClient(config)

    client.login()
    print client.getNamespaceSamples()
    client.logout()

# DAO test
def testDAO():
    resource = {'ecs_ip': '10.1.83.51',
            'api_port': '4443',
            'username': 'jiale-huo-admin',
            'password': 'dangerous',
            'cert_path': '/opt/stack/ecs-mgmt.cer',
            'timezone': 'Asia/Shanghai',
            'frequency': 'Hourly',
            'end_hour': 2,
            'sample_hour': 1,
            'project_id': '1234567890'}

    dao = ecs_billing_dao.ECSBillingDAO(resource)
    vdc_id = dao.getVDCLocalID()
    resource['vdc_id'] = vdc_id
    print dao.getSamples()

cleanup()
# testClient()
testDAO()
