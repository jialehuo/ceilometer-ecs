class ECSManagementConfig:

    def __init__(self, ecs_ip, api_port, username, password, cert_path, timezone='US/Eastern', frequency='Daily', endhour=2, samplehour=3):
        self.ecs_ip = ecs_ip
        self.api_port = api_port
        self.username = username
        self.password = password
        self.cert_path = cert_path
        self.timezone = timezone
        self.frequency = frequency
        self.endhour = endhour
        self.samplehour = samplehour
