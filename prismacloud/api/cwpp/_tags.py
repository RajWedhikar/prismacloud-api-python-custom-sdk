""" Prisma Cloud Compute API Tags Endpoints Class """

# Tags are predefined labels that help you manage your vulnerabilities via the Console UI and Prisma Cloud Compute API.

class TagsPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Tags Endpoints Class """

    def tags_list_read(self, concurrent=False):
        tags = self.execute_compute('GET', 'api/v1/tags', concurrent=concurrent)
        return tags

    def tag_add(self, body_params=None, concurrent=False):
        result = self.execute_compute('POST', 'api/v1/tags', body_params=body_params, concurrent=concurrent)
        return result

    def tag_delete(self, tag_id, concurrent=False):
        result = self.execute_compute('DELETE', 'api/v1/tags/%s' % tag_id, concurrent=concurrent)
        return result

    def tag_update(self, tag_id, body_params, concurrent=False):
        result = self.execute_compute('PUT', 'api/v1/tags/%s' % tag_id, body_params=body_params, concurrent=concurrent)
        return result

    def tag_delete_vulnerability(self, tag_id, body_params, concurrent=False):
        result = self.execute_compute('DELETE', 'api/v1/tags/%s/vuln' % tag_id, body_params=body_params, concurrent=concurrent)
        return result

    def tag_set_vulnerability(self, tag_id, body_params, concurrent=False):
        result = self.execute_compute('POST', 'api/v1/tags/%s/vuln' % tag_id, body_params=body_params, concurrent=concurrent)
        return result
