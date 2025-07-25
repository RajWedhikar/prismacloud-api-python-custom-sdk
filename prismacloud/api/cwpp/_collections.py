""" Prisma Cloud Compute API Collections Endpoints Class """

# Containers

class CollectionsPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Collections Endpoints Class """

    def collections_list_read(self, query_params=None, concurrent=False, max_workers=4):
        return self.execute_compute('GET', 'api/v1/collections', query_params=query_params, paginated=True, concurrent=concurrent, max_workers=max_workers)

    def collection_usages(self, collection_id, concurrent=False, max_workers=4):
        return self.execute_compute('GET', 'api/v1/collections/%s/usages' % collection_id, paginated=True, concurrent=concurrent, max_workers=max_workers)

    # Note: No response is returned upon successful execution of POST, PUT, and DELETE.
    # You must verify the collection via collections_list_read() or the Console.

    def collection_create(self, body_params, concurrent=False, max_workers=4):
        return self.execute_compute('POST', 'api/v1/collections', body_params=body_params, concurrent=concurrent, max_workers=max_workers)

    def collection_update(self, collection_id, body_params, concurrent=False, max_workers=4):
            return self.execute_compute('PUT', 'api/v1/collections/%s' % collection_id, body_params=body_params, concurrent=concurrent, max_workers=max_workers)

    def collection_delete(self, collection_id, concurrent=False, max_workers=4):
        return self.execute_compute('DELETE', 'api/v1/collections/%s' % collection_id, concurrent=concurrent, max_workers=max_workers)
