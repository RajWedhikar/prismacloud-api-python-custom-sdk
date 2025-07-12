""" Requests and Output """

import json
import time
import math
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter, Retry


class PrismaCloudAPICWPPMixin():
    """ Requests and Output """

    def _initialize_enhanced_error_handling(self):
        """Initialize enhanced error handling and retry mechanisms if not already initialized"""
        if not hasattr(self, '_circuit_breaker_state'):
            # Circuit breaker state
            self._circuit_breaker_state = {
                'failures': 0,
                'last_failure_time': None,
                'state': 'CLOSED',  # CLOSED, OPEN, HALF_OPEN
                'threshold': 3,  # Reduced from 5 - fewer failures before opening circuit
                'timeout': 30,  # Reduced from 60 - faster recovery
                'success_threshold': 2  # Successes needed to close circuit
            }
            
            # Rate limiting state
            self._rate_limit_state = {
                'requests': defaultdict(list),
                'max_requests_per_minute': 20,  # Further reduced for stability
                'max_requests_per_second': 2    # Further reduced for stability
            }
            
            # Enhanced retry configuration
            self._retry_config = {
                'max_retries': 3,
                'backoff_factor': 0.5,
                'max_backoff': 60,
                'jitter': True,
                'retry_status_codes': [408, 429, 500, 502, 503, 504],
                'retry_exceptions': [
                    requests.exceptions.ConnectTimeout,
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ChunkedEncodingError
                ]
            }

    def _calculate_backoff(self, attempt, base_delay=1):
        """Calculate exponential backoff with jitter"""
        if attempt <= 0:
            return base_delay
        
        # Exponential backoff: base_delay * 2^attempt
        delay = min(base_delay * (2 ** attempt), self._retry_config['max_backoff'])
        
        # Add jitter to prevent thundering herd
        if self._retry_config['jitter']:
            jitter = random.uniform(0, 0.1 * delay)
            delay += jitter
        
        return delay

    def _check_circuit_breaker(self, endpoint):
        """Check if circuit breaker is open for the endpoint"""
        self._initialize_enhanced_error_handling()
        now = datetime.now()
        state = self._circuit_breaker_state
        
        if state['state'] == 'OPEN':
            if state['last_failure_time'] and (now - state['last_failure_time']).total_seconds() > state['timeout']:
                state['state'] = 'HALF_OPEN'
                state['failures'] = 0
                print(f"🔄 Circuit breaker for {endpoint} moved to HALF_OPEN")
                return False
            else:
                print(f"🚫 Circuit breaker for {endpoint} is OPEN - request blocked")
                return True
        
        return False

    def _record_circuit_breaker_success(self, endpoint):
        """Record a successful request for circuit breaker"""
        self._initialize_enhanced_error_handling()
        state = self._circuit_breaker_state
        if state['state'] == 'HALF_OPEN':
            state['failures'] = 0
            state['state'] = 'CLOSED'
            print(f"✅ Circuit breaker for {endpoint} moved to CLOSED")

    def _record_circuit_breaker_failure(self, endpoint):
        """Record a failed request for circuit breaker"""
        self._initialize_enhanced_error_handling()
        state = self._circuit_breaker_state
        state['failures'] += 1
        state['last_failure_time'] = datetime.now()
        
        if state['state'] == 'HALF_OPEN' or state['failures'] >= state['threshold']:
            state['state'] = 'OPEN'
            print(f"🚨 Circuit breaker for {endpoint} moved to OPEN after {state['failures']} failures")

    def _check_rate_limit(self, endpoint):
        """Check if we're within rate limits"""
        self._initialize_enhanced_error_handling()
        now = datetime.now()
        requests_list = self._rate_limit_state['requests'][endpoint]
        
        # Remove old requests (older than 1 minute)
        requests_list[:] = [req_time for req_time in requests_list 
                           if (now - req_time).total_seconds() < 60]
        
        # Check per-minute limit
        if len(requests_list) >= self._rate_limit_state['max_requests_per_minute']:
            oldest_request = min(requests_list)
            wait_time = 5 - (now - oldest_request).total_seconds()
            if wait_time > 0:
                print(f"⏳ Rate limit reached for {endpoint}, waiting {wait_time:.1f} seconds")
                time.sleep(wait_time)
        
        # Check per-second limit (simple sliding window)
        recent_requests = [req_time for req_time in requests_list 
                          if (now - req_time).total_seconds() < 1]
        if len(recent_requests) >= self._rate_limit_state['max_requests_per_second']:
            time.sleep(0.5)  # Increased delay to avoid overwhelming the API
        
        # Record this request
        requests_list.append(now)

    def _categorize_error(self, response, exception=None):
        """Categorize errors for appropriate handling"""
        if exception:
            if isinstance(exception, requests.exceptions.ConnectTimeout):
                return 'CONNECTION_TIMEOUT'
            elif isinstance(exception, requests.exceptions.ReadTimeout):
                return 'READ_TIMEOUT'
            elif isinstance(exception, requests.exceptions.ConnectionError):
                return 'CONNECTION_ERROR'
            elif isinstance(exception, requests.exceptions.ChunkedEncodingError):
                return 'CHUNKED_ENCODING_ERROR'
            elif isinstance(exception, ValueError):
                return 'JSON_PARSE_ERROR'
            else:
                return 'UNKNOWN_ERROR'
        
        if response:
            status_code = response.status_code
            if status_code == 401:
                return 'AUTHENTICATION_ERROR'
            elif status_code == 403:
                return 'AUTHORIZATION_ERROR'
            elif status_code == 404:
                return 'NOT_FOUND'
            elif status_code == 408:
                return 'REQUEST_TIMEOUT'
            elif status_code == 429:
                return 'RATE_LIMIT_EXCEEDED'
            elif status_code >= 500:
                return 'SERVER_ERROR'
            elif status_code >= 400:
                return 'CLIENT_ERROR'
        
        return 'UNKNOWN_ERROR'

    def _should_retry(self, error_category, attempt):
        """Determine if a request should be retried based on error category and attempt number"""
        if attempt >= self._retry_config['max_retries']:
            return False
        
        # Always retry server errors and connection issues
        if error_category in ['SERVER_ERROR', 'CONNECTION_ERROR', 'CONNECTION_TIMEOUT', 'READ_TIMEOUT', 'CHUNKED_ENCODING_ERROR']:
            return True
        
        # Retry rate limit errors with exponential backoff
        if error_category == 'RATE_LIMIT_EXCEEDED':
            return True
        
        # Retry request timeouts
        if error_category == 'REQUEST_TIMEOUT':
            return True
        
        # Don't retry client errors (except rate limiting)
        if error_category in ['AUTHENTICATION_ERROR', 'AUTHORIZATION_ERROR', 'NOT_FOUND', 'CLIENT_ERROR']:
            return False
        
        return False

    def _handle_authentication_error(self, endpoint):
        """Handle authentication errors by re-logging in"""
        print(f"🔐 Authentication error for {endpoint}, attempting re-login...")
        try:
            self.extend_login_compute()
            print(f"✅ Re-authentication successful for {endpoint}")
            return True
        except Exception as e:
            print(f"❌ Re-authentication failed for {endpoint}: {e}")
            return False

    def _print_progress_bar(self, current, total, start_time, prefix="Progress", endpoint="", records_fetched=0, total_records=0):
        """Print a progress bar with percentage, estimated time, and record information"""
        if total == 0:
            return
        
        percentage = (current / total) * 100
        elapsed_time = time.time() - start_time
        
        if current > 0:
            estimated_total_time = (elapsed_time / current) * total
            remaining_time = estimated_total_time - elapsed_time
            eta_str = f"ETA: {remaining_time:.1f}s"
        else:
            eta_str = "ETA: calculating..."
        
        # Create progress bar (50 characters wide)
        bar_length = 50
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Build the progress line with endpoint and record information
        progress_line = f"\r{prefix}: [{bar}] {current}/{total} ({percentage:.1f}%) | {eta_str}"
        
        if endpoint:
            progress_line += f" | Endpoint: {endpoint}"
        
        if total_records > 0:
            progress_line += f" | Records: {records_fetched}/{total_records}"
        
        print(progress_line, end='', flush=True)
        
        if current == total:
            print()  # New line when complete

    def _verify_threadpool_workers(self, executor, max_workers=4):
        """Verify that ThreadPoolExecutor is using the expected number of workers"""
        actual_workers = executor._max_workers
        if actual_workers != max_workers:
            print(f"⚠️  Warning: Expected {max_workers} workers, but ThreadPoolExecutor has {actual_workers}")
        else:
            print(f"ThreadPoolExecutor confirmed: {actual_workers} workers active")
        return actual_workers

    def login_compute(self):
        if self.api:
            # Login via CSPM.
            self.login()
        elif self.api_compute:
            # Login via CWP.
            self.login('https://%s/api/v1/authenticate' % self.api_compute)
        else:
            self.error_and_exit(
                418, "Specify a Prisma Cloud URL or Prisma Cloud Compute URL")
        self.debug_print('New API Token: %s' % self.token)

    def extend_login_compute(self):
        # There is no extend for CWP, just logon again.
        self.debug_print('Extending API Token')
        self.login_compute()

    def _make_single_request_with_retry(self, action, url, request_headers, query_params, body_params_json, session, endpoint="", max_retries=None):
        """Make a single API request with enhanced retry logic"""
        # Initialize enhanced error handling if not already done
        self._initialize_enhanced_error_handling()
        
        if max_retries is None:
            max_retries = self._retry_config['max_retries']
        
        # Check circuit breaker
        if self._check_circuit_breaker(endpoint):
            raise requests.exceptions.RequestException(f"Circuit breaker is OPEN for {endpoint}")
        
        # Check rate limits
        self._check_rate_limit(endpoint)
        
        for attempt in range(max_retries + 1):
            try:
                # Note: token_timer and token_limit are inherited from the main PrismaCloudAPI class
                if hasattr(self, '_token_lock'):
                    with self._token_lock:
                        if hasattr(self, 'token_timer') and hasattr(self, 'token_limit'):
                            if int(time.time() - self.token_timer) > self.token_limit:
                                self.extend_login_compute()
                        if self.token:
                            if self.api:
                                # Authenticate via CSPM
                                request_headers['x-redlock-auth'] = self.token
                            else:
                                # Authenticate via CWP
                                request_headers['Authorization'] = "Bearer %s" % self.token
                else:
                    # Fallback for when _token_lock is not available
                    if hasattr(self, 'token_timer') and hasattr(self, 'token_limit'):
                        if int(time.time() - self.token_timer) > self.token_limit:
                            self.extend_login_compute()
                    if self.token:
                        if self.api:
                            # Authenticate via CSPM
                            request_headers['x-redlock-auth'] = self.token
                        else:
                            # Authenticate via CWP
                            request_headers['Authorization'] = "Bearer %s" % self.token
                
                self.debug_print('API URL: %s' % url)
                self.debug_print('API Request Headers: (%s)' % request_headers)
                self.debug_print('API Query Params: %s' % query_params)
                self.debug_print('API Body Params: %s' % body_params_json)
                
                api_response = session.request(action, url, headers=request_headers, params=query_params,
                                               data=body_params_json, verify=self.verify, timeout=self.timeout)
                
                self.debug_print('API Response Status Code: (%s)' % api_response.status_code)
                self.debug_print('API Response Headers: (%s)' % api_response.headers)
                
                if api_response.ok:
                    self._record_circuit_breaker_success(endpoint)
                    
                    if not api_response.content:
                        return None
                    if api_response.headers.get('Content-Type') == 'application/x-gzip':
                        return api_response.content
                    if api_response.headers.get('Content-Type') == 'text/csv':
                        return api_response.content.decode('utf-8')
                    try:
                        result = json.loads(api_response.content)
                        return result
                    except ValueError:
                        self.logger.error('JSON raised ValueError, API: (%s) with query params: (%s) and body params: (%s) parsing response: (%s)' % (
                            url, query_params, body_params_json, api_response.content))
                        raise ValueError('JSON parsing failed')
                else:
                    error_category = self._categorize_error(api_response)
                    
                    # Handle authentication errors specially
                    if error_category == 'AUTHENTICATION_ERROR':
                        if self._handle_authentication_error(endpoint):
                            continue  # Retry immediately after re-authentication
                        else:
                            self._record_circuit_breaker_failure(endpoint)
                            raise requests.exceptions.RequestException(f'Authentication failed: {api_response.status_code}')
                    
                    # Check if we should retry
                    if self._should_retry(error_category, attempt):
                        backoff_delay = self._calculate_backoff(attempt)
                        print(f"⚠️  {error_category} for {endpoint} (attempt {attempt + 1}/{max_retries + 1}), retrying in {backoff_delay:.1f}s...")
                        time.sleep(backoff_delay)
                        continue
                    else:
                        self._record_circuit_breaker_failure(endpoint)
                        self.logger.error('API: (%s) responded with a status of: (%s), with query: (%s) and body params: (%s)' % (
                            url, api_response.status_code, query_params, body_params_json))
                        raise requests.exceptions.RequestException(f'API responded with status {api_response.status_code}: {api_response.text}')
                        
            except Exception as e:
                error_category = self._categorize_error(None, e)
                
                # Check if we should retry
                if self._should_retry(error_category, attempt):
                    backoff_delay = self._calculate_backoff(attempt)
                    print(f"⚠️  {error_category} for {endpoint} (attempt {attempt + 1}/{max_retries + 1}), retrying in {backoff_delay:.1f}s...")
                    time.sleep(backoff_delay)
                    continue
                else:
                    self._record_circuit_breaker_failure(endpoint)
                    self.logger.error('Request failed for %s: %s' % (endpoint, str(e)))
                    raise e
        
        # If we get here, all retries failed
        self._record_circuit_breaker_failure(endpoint)
        raise requests.exceptions.RequestException(f'All {max_retries + 1} attempts failed for {endpoint}')

    def _make_single_request(self, action, url, request_headers, query_params, body_params_json, session):
        """Make a single API request - used for concurrent execution (legacy method)"""
        return self._make_single_request_with_retry(action, url, request_headers, query_params, body_params_json, session)

    # pylint: disable=too-many-arguments,too-many-branches,too-many-locals,too-many-statements
    def execute_compute(self, action, endpoint, query_params=None, body_params=None, request_headers=None, force=False, paginated=False, concurrent=False, max_workers=4):
        self.suppress_warnings_when_verify_false()
        if not self.token:
            self.login_compute()
        if not request_headers:
            request_headers = {'Content-Type': 'application/json'}
        if body_params:
            body_params_json = json.dumps(body_params)
        else:
            body_params_json = None
        # Set User Agent
        request_headers['User-Agent'] = "W"
        # Endpoints that return large numbers of results use a 'Total-Count' response header.
        # Pagination is via query parameters for both GET and POST, and the limit has a maximum of 50.
        offset = 0
        limit = 100
        results = []

        # Enhanced retry configuration with exponential backoff
        retries = Retry(
            total=self.retry_number,
            status_forcelist=self.retry_status_codes, 
            raise_on_status=False,
            backoff_factor=self._retry_config['backoff_factor'],
            allowed_methods=['GET', 'POST', 'PUT', 'DELETE']
        )

        with requests.Session() as session:
            # Enhanced connection pooling
            adapter = HTTPAdapter(
                max_retries=retries,
                pool_connections=10,
                pool_maxsize=20,
                pool_block=False
            )
            session.mount('https://%s/%s' % (self.api_compute, endpoint), adapter=adapter)

            # If not paginated or not concurrent, use the original sequential approach
            if not paginated or not concurrent:
                # Initialize timing variables for all sequential operations
                sequential_start_time = time.time()
                if paginated and not concurrent:
                    print(f"🔄 Starting sequential pagination for endpoint: {endpoint}")
                more = False
                page_count = 0
                total_records_fetched = 0
                total_available_records = 0
                while offset == 0 or more is True:
                    if int(time.time() - self.token_timer) > self.token_limit:
                        self.extend_login_compute()
                    if paginated:
                        url = 'https://%s/%s?limit=%s&offset=%s' % (
                            self.api_compute, endpoint, limit, offset)
                    else:
                        url = 'https://%s/%s' % (self.api_compute, endpoint)
                    if self.token:
                        if self.api:
                            # Authenticate via CSPM
                            request_headers['x-redlock-auth'] = self.token
                        else:
                            # Authenticate via CWP
                            request_headers['Authorization'] = "Bearer %s" % self.token
                    self.debug_print('API URL: %s' % url)
                    self.debug_print('API Request Headers: (%s)' % request_headers)
                    self.debug_print('API Query Params: %s' % query_params)
                    self.debug_print('API Body Params: %s' % body_params_json)
                    # Add User-Agent to the headers
                    request_headers['User-Agent'] = self.user_agent
                    
                    try:
                        api_response = session.request(action, url, headers=request_headers, params=query_params,
                                                       data=body_params_json, verify=self.verify, timeout=self.timeout)
                        self.debug_print('API Response Status Code: (%s)' %
                                         api_response.status_code)
                        self.debug_print('API Response Headers: (%s)' %
                                         api_response.headers)
                        if api_response.ok:
                            if not api_response.content:
                                return None
                            if api_response.headers.get('Content-Type') == 'application/x-gzip':
                                return api_response.content
                            if api_response.headers.get('Content-Type') == 'text/csv':
                                return api_response.content.decode('utf-8')
                            try:
                                result = json.loads(api_response.content)
                            except ValueError:
                                self.logger.error('JSON raised ValueError, API: (%s) with query params: (%s) and body params: (%s) parsing response: (%s)' % (
                                    url, query_params, body_params, api_response.content))
                                if force:
                                    return results  # or continue
                                self.error_and_exit(api_response.status_code, 'JSON raised ValueError, API: (%s) with query params: (%s) and body params: (%s) parsing response: (%s)' % (
                                    url, query_params, body_params, api_response.content))
                            if 'Total-Count' in api_response.headers:
                                page_count += 1
                                total_count = int(api_response.headers['Total-Count'])
                                total_available_records = total_count
                                
                                if total_count > 0:
                                    if isinstance(result, list):
                                        total_records_fetched += len(result)
                                    else:
                                        total_records_fetched += 1
                                    results.extend(result)
                                
                                offset += limit
                                more = bool(offset < total_count)
                                
                                if more:
                                    # Calculate total pages for progress bar
                                    total_pages = math.ceil(total_count / limit)
                                    self._print_progress_bar(
                                        page_count, 
                                        total_pages, 
                                        sequential_start_time, 
                                        "Sequential Pages",
                                        endpoint,
                                        total_records_fetched,
                                        total_available_records
                                    )
                            else:
                                if paginated and not concurrent:
                                    sequential_total_time = time.time() - sequential_start_time
                                    print(f"\n✅ Sequential pagination completed: {page_count + 1} pages in {sequential_total_time:.2f} seconds")
                                    print(f"📊 Total records fetched: {total_records_fetched}")
                                return result
                        else:
                            self.logger.error('API: (%s) responded with a status of: (%s), with query: (%s) and body params: (%s)' % (
                                url, api_response.status_code, query_params, body_params))
                            if force:
                                return results
                            self.error_and_exit(api_response.status_code, 'API: (%s) with query params: (%s) and body params: (%s) responded with an error and this response:\n%s' % (
                                url, query_params, body_params, api_response.text))
                    except Exception as e:
                        self.logger.error('Request failed for %s: %s' % (endpoint, str(e)))
                        if force:
                            return results
                        raise e
                return results

            # Concurrent pagination approach
            else:
                print(f"🔄 Starting concurrent pagination for endpoint: {endpoint}")
                
                # First, get the total count to determine how many pages we need
                initial_url = 'https://%s/%s?limit=%s&offset=0' % (self.api_compute, endpoint, limit)
                try:
                    print(f"📊 Fetching initial page to determine total count for endpoint: {endpoint}")
                    
                    # Make the initial request to get total count
                    initial_headers = request_headers.copy()
                    if self.token:
                        if self.api:
                            initial_headers['x-redlock-auth'] = self.token
                        else:
                            initial_headers['Authorization'] = "Bearer %s" % self.token
                    
                    initial_result = self._make_single_request_with_retry(
                        action, initial_url, initial_headers, query_params, body_params_json, session, endpoint
                    )
                    
                    if not initial_result:
                        return []
                    
                    # Check if we have pagination headers (we need to make a separate request to get headers)
                    try:
                        initial_response = session.request(action, initial_url, headers=initial_headers, params=query_params,
                                                          data=body_params_json, verify=self.verify, timeout=self.timeout)
                        
                        if 'Total-Count' not in initial_response.headers:
                            print("✅ Single page result - no pagination needed")
                            return initial_result
                        
                        total_count = int(initial_response.headers['Total-Count'])
                        print(f"📈 Total records found: {total_count} for endpoint: {endpoint}")
                        
                        if total_count <= limit:
                            print(f"✅ All data in first page for endpoint: {endpoint} - no additional requests needed")
                            return initial_result
                        
                        # Calculate all the offsets we need to fetch
                        offsets = list(range(limit, total_count, limit))
                        total_pages = len(offsets) + 1  # +1 for the initial page
                        
                        print(f"📄 Fetching {len(offsets)} additional pages concurrently (using {max_workers} threads) for endpoint: {endpoint}")
                        
                        # Use ThreadPoolExecutor for concurrent requests
                        concurrent_start_time = time.time()
                        with ThreadPoolExecutor(max_workers=max_workers) as executor:
                            # Verify ThreadPool configuration
                            actual_workers = self._verify_threadpool_workers(executor, max_workers=max_workers)
                            
                            # Submit all the concurrent requests with small delays to prevent overwhelming the API
                            future_to_offset = {}
                            for i, offset_val in enumerate(offsets):
                                url = 'https://%s/%s?limit=%s&offset=%s' % (self.api_compute, endpoint, limit, offset_val)
                                future = executor.submit(
                                    self._make_single_request_with_retry, 
                                    action, 
                                    url, 
                                    request_headers.copy(), 
                                    query_params, 
                                    body_params_json, 
                                    session,
                                    endpoint
                                )
                                future_to_offset[future] = offset_val
                                
                                # Add small delay between submissions to prevent overwhelming the API
                                if i < len(offsets) - 1:  # Don't delay after the last request
                                    time.sleep(0.1)  # 100ms delay between request submissions
                            
                            print(f"🚀 Submitted {len(future_to_offset)} concurrent requests to {actual_workers} workers for endpoint: {endpoint}")
                            print("📊 Progress bar:")
                            
                            # Collect results as they complete
                            all_results = [initial_result]  # Start with the first page
                            completed_pages = 1
                            # Handle different result types for record counting
                            if isinstance(initial_result, list):
                                total_records_fetched = len(initial_result)
                            elif isinstance(initial_result, str):
                                # For CSV data, count lines (excluding header)
                                lines = initial_result.strip().split('\n')
                                total_records_fetched = max(0, len(lines) - 1)  # Subtract header
                            else:
                                total_records_fetched = 1
                            failed_requests = []
                            
                            for future in as_completed(future_to_offset):
                                offset_val = future_to_offset[future]
                                completed_pages += 1
                                
                                try:
                                    result = future.result()
                                    if result:
                                        # Handle different result types for record counting
                                        if isinstance(result, list):
                                            total_records_fetched += len(result)
                                        elif isinstance(result, str):
                                            # For CSV data, count lines (excluding header)
                                            lines = result.strip().split('\n')
                                            total_records_fetched += max(0, len(lines) - 1)  # Subtract header
                                        else:
                                            total_records_fetched += 1
                                        all_results.append(result)
                                        # Update progress bar with endpoint and record information
                                        self._print_progress_bar(
                                            completed_pages, 
                                            total_pages, 
                                            concurrent_start_time, 
                                            "Concurrent Pages",
                                            endpoint,
                                            total_records_fetched,
                                            total_count
                                        )
                                    else:
                                        all_results.append([])  # Empty result
                                        self._print_progress_bar(
                                            completed_pages, 
                                            total_pages, 
                                            concurrent_start_time, 
                                            "Concurrent Pages",
                                            endpoint,
                                            total_records_fetched,
                                            total_count
                                        )
                                except Exception as exc:
                                    failed_requests.append((offset_val, exc))
                                    print(f"\n❌ Error at offset {offset_val} for endpoint {endpoint}: {exc}")
                                    self.logger.error('Request for offset %s generated an exception: %s' % (offset_val, exc))
                                    if not force:
                                        raise exc
                            
                            concurrent_total_time = time.time() - concurrent_start_time
                            print(f"\n✅ Concurrent execution completed in {concurrent_total_time:.2f} seconds for endpoint: {endpoint}")
                            print(f"📊 Total records fetched: {total_records_fetched}")
                            
                            if failed_requests:
                                print(f"⚠️  {len(failed_requests)} requests failed out of {total_pages} total pages")
                            
                            print("🔄 Combining results from all pages...")
                            
                            # Combine all results
                            combined_results = []
                            for result_batch in all_results:
                                if isinstance(result_batch, list):
                                    combined_results.extend(result_batch)
                                else:
                                    combined_results.append(result_batch)
                            
                            print(f"✅ Successfully retrieved {len(combined_results)} total records from {total_pages} pages")
                            return combined_results
                    
                    except Exception as exc:
                        self.logger.error('Failed to get pagination headers: %s' % exc)
                        if force:
                            return initial_result
                        raise exc
                
                except Exception as exc:
                    self.logger.error('Concurrent execution failed: %s' % exc)
                    if not force:
                        raise exc
                    return results

    # The Compute API setting is optional.

    def validate_api_compute(self):
        if not self.api_compute:
            self.error_and_exit(
                500, 'Please specify a Prisma Cloud Compute API URL.')

    # Exit handler (Error).

    @classmethod
    def error_and_exit(cls, error_code, error_message='', system_message=''):
        raise SystemExit('\n\nStatus Code: %s\n%s\n%s\n' %
                         (error_code, error_message, system_message))
