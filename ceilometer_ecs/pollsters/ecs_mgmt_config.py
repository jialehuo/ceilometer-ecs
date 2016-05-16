class ECSManagementConfig:

    def __init__(self, ecs_ip, api_port, username, password, cert_path):
        self.ecs_ip = ecs_ip
        self.api_port = api_port
        self.username = username
        self.password = password
        self.cert_path = cert_path
