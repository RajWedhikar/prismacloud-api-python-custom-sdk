""" Prisma Cloud Compute API Defenders Endpoints Class """

# Containers

class DefendersPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Defenders Endpoints Class """

    def defenders_list_read(self, query_params=None, concurrent=False, max_workers=4):
        defenders = self.execute_compute('GET', 'api/v1/defenders', query_params=query_params, paginated=True, concurrent=concurrent, max_workers=max_workers)
        return defenders

    def defenders_names_list_read(self, query_params=None, concurrent=False, max_workers=4):
        defenders = self.execute_compute('GET', 'api/v1/defenders/names', query_params=query_params, paginated=False, concurrent=concurrent)
        return defenders
