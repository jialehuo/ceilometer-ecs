import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'pollsters'))
import ecs_billing_dao

resource = {'ecs_ip': '10.1.83.51',
            'api_port': '4443',
            'username': 'jiale-huo-admin',
            'password': 'dangerous',
            'cert_path': '/opt/stack/ecs-mgmt.cer'}

dao = ecs_billing_dao.ECSBillingDAO(resource)

print dao.getSamples()
