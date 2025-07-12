""" Prisma Cloud Compute API Stats Endpoints Class """

class StatsPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute API Stats Endpoints Class """

    def stats_app_firewall_count_read(self, concurrent=False):
        # Returns the number of app firewalls in use.
        return self.execute_compute('GET', 'api/v1/stats/app-firewall/count', concurrent=concurrent)

    def stats_compliance_read(self, query_params=None, concurrent=False):
        # Maps to the table in Monitor > Compliance > Compliance Explorer
        return self.execute_compute('GET', 'api/v1/stats/compliance?', query_params=query_params, concurrent=concurrent)

    def stats_compliance_download(self, query_params=None, concurrent=False):
        return self.execute_compute('GET', 'api/v1/stats/compliance/download?', query_params=query_params, concurrent=concurrent)

    def stats_compliance_refresh(self, query_params=None, concurrent=False):
        # Refreshes the current day's list and counts of compliance issues, as well as the list of affected running resources.
        # This endpoint returns the same response as /api/v1/stats/compliance, but with updated data for the current day.
        return self.execute_compute('GET', 'api/v1/stats/compliance/refresh?', query_params=query_params, concurrent=concurrent)

    def stats_daily_read(self, concurrent=False):
        # Returns a historical list of per-day statistics for the resources protected by Prisma Cloud Compute,
        # including the total number of runtime audits, image vulnerabilities, and compliance violations.
        return self.execute_compute('GET', 'api/v1/stats/daily', paginated=True, concurrent=concurrent)

    def stats_trends_read(self, concurrent=False):
        # Returns statistics about the resources protected by Prisma Cloud Compute,
        # including the total number of runtime audits, image vulnerabilities, and compliance violations.
        return self.execute_compute('GET', 'api/v1/stats/dashboard', concurrent=concurrent)

    def stats_events_read(self, query_params=None, concurrent=False):
        # Returns events statistics for your environment.
        return self.execute_compute('GET', 'api/v1/stats/events?', query_params=query_params, concurrent=concurrent)

    def stats_license_read(self, concurrent=False):
        return self.execute_compute('GET', 'api/v1/stats/license', concurrent=concurrent)

    def stats_vulnerabilities_read(self, query_params=None, concurrent=False):
        # Returns a list of vulnerabilities (CVEs) in the deployed images, registry images, hosts, and serverless functions affecting your environment.
        return self.execute_compute('GET', 'api/v1/stats/vulnerabilities?', query_params=query_params, paginated=True, concurrent=concurrent)

    def stats_vulnerabilities_download(self, query_params=None, concurrent=False):
        return self.execute_compute('GET', 'api/v1/stats/vulnerabilities/download?', query_params=query_params, concurrent=concurrent)

    def stats_vulnerabilities_impacted_resoures_read(self, query_params=None, concurrent=False):
        # Generates a list of impacted resources for a specific vulnerability. This endpoint returns a list of all deployed images, registry images, hosts, and serverless functions affected by a given CVE.
        return self.execute_compute('GET', 'api/v1/stats/vulnerabilities/impacted-resources?', query_params=query_params, concurrent=concurrent)

    def stats_vulnerabilities_impacted_resoures_download(self, query_params=None, concurrent=False):
        return self.execute_compute('GET', 'api/v1/stats/vulnerabilities/impacted-resources/download?', query_params=query_params, concurrent=concurrent)

    def stats_vulnerabilities_refresh(self, query_params=None, concurrent=False):
        # Refreshes the current day's CVE counts and CVE list, as well as their descriptions.
        # This endpoint returns the same response as /api/v1/stats/vulnerabilities, but with updated data for the current day.
        return self.execute_compute('GET', 'api/v1/stats/vulnerabilities/refresh?', query_params=query_params, paginated=True, concurrent=concurrent)
