""" Prisma Cloud Compute API Settings Endpoints Class """

# Credentials (Defend > Compliance)

class SettingsPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Settings Endpoints Class """

    def settings_serverless_scan_read(self, concurrent=False):
        return self.execute_compute('get', 'api/v1/settings/serverless-scan', concurrent=concurrent)

    def settings_serverless_scan_write(self, body, concurrent=False):
        return self.execute_compute(
            'put', 'api/v1/settings/serverless-scan',
            body_params=body, concurrent=concurrent
        )

    def settings_registry_read(self, concurrent=False):
        return self.execute_compute('get', 'api/v1/settings/registry', concurrent=concurrent)

    def settings_registry_write(self, body, concurrent=False):
        return self.execute_compute(
            'put', 'api/v1/settings/registry',
            body_params=body, concurrent=concurrent
        )

    def settings_host_auto_deploy_read(self, concurrent=False):
        return self.execute_compute('get', 'api/v1/settings/host-auto-deploy', concurrent=concurrent)

    def settings_host_auto_deploy_write(self, body, concurrent=False):
        return self.execute_compute(
            'post', 'api/v1/settings/host-auto-deploy',
            body_params=body, concurrent=concurrent
        )

    def settings_serverless_auto_deploy_read(self, concurrent=False):
        return self.execute_compute('get', 'api/v1/settings/serverless-auto-deploy', concurrent=concurrent)

    def settings_serverless_auto_deploy_write(self, body, concurrent=False):
        return self.execute_compute(
            'post', 'api/v1/settings/serverless-auto-deploy',
            body_params=body, concurrent=concurrent
        )
