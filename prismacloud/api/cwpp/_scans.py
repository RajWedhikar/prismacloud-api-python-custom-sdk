""" Prisma Cloud Compute API Scans Endpoints Class """

# Scans (Monitor > Vulnerabilities/Compliance > Images > CI)

class ScansPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Scans Endpoints Class """

    def scans_list_read(self, image_id=None, concurrent=False, max_workers=4):
        if image_id:
            images = self.execute_compute('GET', 'api/v1/scans?imageID=%s&filterBaseImage=true' % image_id, concurrent=concurrent, max_workers=max_workers)
        else:
            images = self.execute_compute('GET', 'api/v1/scans?filterBaseImage=true', paginated=True, concurrent=concurrent, max_workers=max_workers)
        return images
