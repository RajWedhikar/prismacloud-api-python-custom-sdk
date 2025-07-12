""" Prisma Cloud Compute API Images Endpoints Class """

import urllib.parse

# Credentials (Manage > Authentication > Credentials store)


class CredentialsPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Credentials Endpoints Class """

    def credential_list_read(self, concurrent=False, max_workers=4):
        return self.execute_compute('GET', 'api/v1/credentials', concurrent=concurrent, max_workers=max_workers)

    def credential_list_create(self, body, concurrent=False, max_workers=4):
        return self.execute_compute(
            'POST', 'api/v1/credentials?project=Central+Console',
            body_params=body, concurrent=concurrent, max_workers=max_workers
        )

    def credential_list_delete(self, cred, concurrent=False, max_workers=4):
        return self.execute_compute(
            'DELETE', 'api/v1/credentials/%s' % urllib.parse.quote(cred), concurrent=concurrent, max_workers=max_workers
        )

    def credential_list_usages_read(self, cred, concurrent=False, max_workers=4):
        return self.execute_compute(
            'GET', 'api/v1/credentials/%s/usages' % urllib.parse.quote(cred), concurrent=concurrent, max_workers=max_workers
        )
