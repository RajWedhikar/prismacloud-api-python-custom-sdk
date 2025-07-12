""" Prisma Cloud Compute API Statuses Endpoints Class """

class StatusPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Statuses Endpoints Class """

    def statuses_intelligence(self, concurrent=False):
        return self.execute_compute('GET', 'api/v1/statuses/intelligence', concurrent=concurrent)

    def statuses_registry(self, concurrent=False):
        return self.execute_compute('GET', 'api/v1/statuses/registry', concurrent=concurrent)
