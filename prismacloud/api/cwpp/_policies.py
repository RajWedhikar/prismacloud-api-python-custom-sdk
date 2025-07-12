""" Prisma Cloud Compute API Policies Endpoints Class """

# Credentials (Defend > Compliance)

class PoliciesPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Credentials Endpoints Class """

    def policies_cloud_platforms_read(self, concurrent=False):
        return self.execute_compute('GET', 'api/v1/policies/cloud-platforms', concurrent=concurrent)

    def policies_cloud_platforms_write(self, body_params, concurrent=False):
        return self.execute_compute('PUT', 'api/v1/policies/cloud-platforms', body_params=body_params, concurrent=concurrent)

    # These implement multiple endpoints. See: https://prisma.pan.dev/api/cloud/cwpp/policies

    def policies_read(self, policy_path, concurrent=False):
        return self.execute_compute('GET', 'api/v1/policies/%s' % policy_path, concurrent=concurrent)

    def policies_write(self, policy_path, body_params, concurrent=False):
        return self.execute_compute('PUT', 'api/v1/policies/%s' % policy_path, body_params=body_params, concurrent=concurrent)

    def policies_delete(self, policy_path, concurrent=False):
        return self.execute_compute('PUT', 'api/v1/policies/%s' % policy_path, body_params={}, concurrent=concurrent)
