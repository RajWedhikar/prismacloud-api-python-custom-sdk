""" Prisma Cloud Compute API Logs Endpoints Class """

# Containers

class LogsPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Logs Endpoints Class """

    # Undocumented endpoints.

    def agentless_logs_read(self, query_params=None, concurrent=False, max_workers=4):
        logs = self.execute_compute('GET', 'api/v1/logs/agentless/download', query_params=query_params, concurrent=concurrent, max_workers=max_workers)
        return logs

    def defender_logs_list_read(self, host_name, query_params=None, concurrent=False, max_workers=4):
        logs = self.execute_compute('GET', 'api/v1/logs/defender/download?hostname=%s' % host_name, query_params=query_params, concurrent=concurrent, max_workers=max_workers)
        return logs

    def console_logs_list_read(self, query_params=None, concurrent=False, max_workers=4):
        logs = self.execute_compute('GET', 'api/v1/logs/console', query_params=query_params, concurrent=concurrent, max_workers=max_workers)
        return logs

    def system_logs_list_read(self, query_params=None, concurrent=False, max_workers=4):
        logs = self.execute_compute('GET', 'api/v1/logs/system/download', query_params=query_params, concurrent=concurrent, max_workers=max_workers)
        return logs
