class ECSResource:

    def __init__(self, ecs_endpoint, ecs_username, ecs_password, ecs_cert_path, sample_start_time, sample_interval, sample_delay, ceilometer_endpoint, os_project_name, os_project_domain_name, os_username, os_password, os_user_domain_name, os_auth_url):
        # ECS parameters
        self.ecs_endpoint = ecs_endpoint
        self.ecs_username = ecs_username
        self.ecs_password = ecs_password
        self.ecs_cert_path = ecs_cert_path
        self.ecs_vdc_id = ''

        # Sampling parameters
        self.sample_start_time = sample_start_time
        self.sample_interval = sample_interval
        self.sample_delay = sample_delay

        # OpenStack parameters
        self.ceilometer_endpoint = ceilometer_endpoint
        self.os_project_name = os_project_name
        self.os_project_domain_name = os_project_domain_name
        self.os_username = os_username
        self.os_password = os_password
        self.os_user_domain_name = os_user_domain_name
        self.os_auth_url = os_auth_url 
