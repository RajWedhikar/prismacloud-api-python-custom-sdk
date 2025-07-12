""" Prisma Compute API Cloud Endpoints Class """

# Cloud

class CloudPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Cloud Endpoints Class """

    def cloud_discovery_read(self, concurrent=False, max_workers=4):
        return self.execute_compute('GET', 'api/v1/cloud/discovery', concurrent=concurrent, max_workers=max_workers)

    def cloud_discovery_download(self, query_params=None, concurrent=False, max_workers=4):
        # request_headers = {'Content-Type': 'text/csv'}
        # return self.execute_compute('GET', 'api/v1/cloud/discovery/download?', request_headers=request_headers, query_params=query_params)
        return self.execute_compute('GET', 'api/v1/cloud/discovery/download', query_params=query_params, concurrent=concurrent, max_workers=max_workers)

    def cloud_discovery_scan(self, concurrent=False, max_workers=4):
        return self.execute_compute('POST', 'api/v1/cloud/discovery/scan', concurrent=concurrent, max_workers=max_workers)

    def cloud_discovery_scan_stop(self, concurrent=False, max_workers=4):
        return self.execute_compute('POST', 'api/v1/cloud/discovery/stop', concurrent=concurrent, max_workers=max_workers)

    def cloud_discovery_vms(self, query_params=None, concurrent=False, max_workers=4):
        return self.execute_compute('GET', 'api/v1/cloud/discovery/vms', query_params=query_params, paginated=True, concurrent=concurrent, max_workers=max_workers)

    def cloud_discovery_entities(self, query_params=None, concurrent=False, max_workers=4):
        return self.execute_compute('GET', 'api/v1/cloud/discovery/entities', query_params=query_params, concurrent=concurrent, max_workers=max_workers)
