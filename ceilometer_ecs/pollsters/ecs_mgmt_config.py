class ECSManagementConfig:

    def __init__(self, ecs_ip, api_port, username, password, cert_path, start_time, interval, sample_delay, cache_dir):
        self.ecs_ip = ecs_ip
        self.api_port = api_port
        self.username = username
        self.password = password
        self.cert_path = cert_path
        self.start_time = start_time
        self.interval = interval
        self.sample_delay = sample_delay
        self.cache_dir = cache_dir
