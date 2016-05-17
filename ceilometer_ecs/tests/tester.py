import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pollsters'))
import ecs_billing_dao
import ecs_mgmt_client
import ecs_mgmt_config

resource = {'ecs_ip': '10.1.83.51',
            'api_port': '4443',
            'username': 'jiale-huo-admin',
            'password': 'dangerous',
            'cert_path': '/opt/stack/ecs-mgmt.cer',
            'project_id': '1234567890'}

dao = ecs_billing_dao.ECSBillingDAO(resource)
vdc_id = dao.getVDCLocalID()
resource['vdc_id'] = vdc_id
print dao.getSamples()
