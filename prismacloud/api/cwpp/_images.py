""" Prisma Cloud Compute API Images Endpoints Class """

# Images (Monitor > Vulnerabilities/Compliance > Images > Deployed)

class ImagesPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Images Endpoints Class """

    def images_list_read(self, image_id=None, query_params=None, concurrent=False, max_workers=4):
        if image_id:
            images = self.execute_compute('GET', 'api/v1/images?id=%s' % image_id, query_params=query_params, concurrent=concurrent, max_workers=max_workers)
        else:
            images = self.execute_compute('GET', 'api/v1/images?', query_params=query_params, paginated=True, concurrent=concurrent, max_workers=max_workers)
        return images

    def images_download(self, query_params=None, concurrent=False, max_workers=4):
        images = self.execute_compute('GET', 'api/v1/images/download?', query_params=query_params, concurrent=concurrent, max_workers=max_workers)
        return images
