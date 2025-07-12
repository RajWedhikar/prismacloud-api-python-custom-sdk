""" Prisma Cloud Compute API Images Endpoints Class """

# Images (Monitor > Vulnerabilities/Compliance > Images > Deployed)

class RegistryPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Images Endpoints Class """

    def registry_list_read(self, image_id=None, concurrent=False, max_workers=4):
        if image_id:
            images = self.execute_compute('GET', 'api/v1/registry?id=%s&filterBaseImage=true' % image_id, concurrent=concurrent, max_workers=max_workers)
        else:
            images = self.execute_compute('GET', 'api/v1/registry?filterBaseImage=true', paginated=True, concurrent=concurrent, max_workers=max_workers)
        return images

    def registry_list_image_names(self, query_params=None, concurrent=False, max_workers=4):
        result = self.execute_compute('GET', 'api/v1/registry/names?', query_params=query_params, concurrent=concurrent, max_workers=max_workers)
        return result

    def registry_scan(self, body_params=None, concurrent=False, max_workers=4):
        result = self.execute_compute('POST', 'api/v1/registry/scan', body_params=body_params, concurrent=concurrent, max_workers=max_workers)
        return result

    def registry_scan_select(self, body_params=None, concurrent=False, max_workers=4):
        result = self.execute_compute('POST', 'api/v1/registry/scan/select', body_params=body_params, concurrent=concurrent, max_workers=max_workers)
        return result
