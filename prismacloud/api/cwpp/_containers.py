""" Prisma Cloud Compute API Containers Endpoints Class """

# Containers

class ContainersPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Containers Endpoints Class """

    def containers_list_read(self, image_id=None, query_params=None, concurrent=False, max_workers=4):
        if image_id:
            containers = self.execute_compute('GET', 'api/v1/containers?imageId=%s' % image_id, query_params=query_params, paginated=True, concurrent=concurrent, max_workers=max_workers)
        else:
            containers = self.execute_compute('GET', 'api/v1/containers?', query_params=query_params, paginated=True, concurrent=concurrent, max_workers=max_workers)
        return containers
