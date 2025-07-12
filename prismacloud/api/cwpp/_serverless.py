class ServerlessPrismaCloudAPICWPPMixin:
    """ Prisma Cloud Compute Serverless Endpoints Class """

    # Get serverless function scan results
    def serverless_list_read(self, query_params=None, concurrent=False, max_workers=4):
        result = self.execute_compute('GET', 'api/v1/serverless', query_params=query_params, paginated=True, concurrent=concurrent, max_workers=max_workers)
        return result
   
    # Download serverless function scan results
    def serverless_download(self, query_params=None, concurrent=False, max_workers=4):
        result = self.execute_compute('GET', 'api/v1/serverless/download?', query_params=query_params, concurrent=concurrent, max_workers=max_workers)
        return result
   
    # Start serverless function scan
    def serverless_start_scan(self, concurrent=False, max_workers=4):
        result = self.execute_compute('POST', 'api/v1/serverless/scan', concurrent=concurrent, max_workers=max_workers)
        return result
   
    # Stop serverless function scan
    def serverless_stop_scan(self, concurrent=False, max_workers=4):
        result = self.execute_compute('POST', 'api/v1/serverless/stop', concurrent=concurrent, max_workers=max_workers)
        return result
 