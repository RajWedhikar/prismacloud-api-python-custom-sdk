# Python SDK for the Prisma Cloud APIs

This project includes a Python SDK for the Prisma Cloud APIs (CSPM, CWPP, and CCS) in the form of a Python package.
It also includes reference scripts that utilize this SDK.

Major changes with Version 5.0:

* Command-line argument and configuration file changes.

## Table of Contents

* [Setup](#Setup)
* [Support](#Support)


## Setup

Install the SDK via `pip3`:

```
pip3 install prismacloud-api
```

Please refer to [PyPI](https://pypi.org/project/prismacloud-api) for details.

### Example Scripts

Please refer to this [scripts](https://github.com/PaloAltoNetworks/prismacloud-api-python/tree/main/scripts) directory for configuration, documentation, and usage.

If you prefer to use this SDK without using command-line options, consider these minimal examples:

#### Prisma Cloud Enterprise Edition

```
import os
from prismacloud.api import pc_api

# Settings for Prisma Cloud Enterprise Edition

settings = {
    "url":      "https://api.prismacloud.io/",
    "identity": "access_key",
    "secret":   "secret_key"
}

pc_api.configure(settings)

print('Prisma Cloud API Current User:')
print()
print(pc_api.current_user())
print()
print('Prisma Cloud Compute API Intelligence:')
print()
print(pc_api.statuses_intelligence())
print()

print('Prisma Cloud API Object:')
print()
print(pc_api)
print()
```

#### Prisma Cloud Compute Edition

```
import os
from prismacloud.api import pc_api

# Settings for Prisma Cloud Compute Edition

settings = {
    "url":      "https://console.example.com/",
    "identity": "username",
    "secret":   "password"
}

pc_api.configure(settings)

print('Prisma Cloud Compute API Intelligence:')
print()
print(pc_api.statuses_intelligence())
print()

print('Prisma Cloud API Object:')
print()
print(pc_api)
print()
```

#### CWPP Concurrent Execution

The CWPP (Compute Workload Protection Platform) endpoints support concurrent execution for improved performance when fetching large datasets. You can enable concurrent execution and configure the number of worker threads:

```
# Basic concurrent execution (uses default 4 workers)
hosts = pc_api.hosts_list_read(concurrent=True)

# Custom worker count for concurrent execution
hosts = pc_api.hosts_list_read(concurrent=True, max_workers=3)

# Sequential execution (default behavior)
hosts = pc_api.hosts_list_read(concurrent=False)

# Available CWPP endpoints with concurrent support:
# - hosts_list_read()
# - hosts_info_list_read() 
# - containers_list_read()
# - images_list_read()
# - defenders_list_read()
# - registry_list_read()
# - collections_list_read()
# - audits_list_read()
# - scans_list_read()
# - serverless_list_read()
# - vms_list_read()
# - vulnerabilities_list_read()
# - tags_list_read()
# - cloud_discovery_vms()
# - stats_daily_read()
# - stats_vulnerabilities_read()
# - stats_vulnerabilities_refresh_read()

# Example: Fetch all hosts with 5 concurrent workers
print('Fetching hosts with concurrent execution...')
hosts = pc_api.hosts_list_read(concurrent=True, max_workers=5)
print(f'Retrieved {len(hosts)} hosts')

# Example: Fetch containers with default concurrent settings
print('Fetching containers...')
containers = pc_api.containers_list_read(concurrent=True)
print(f'Retrieved {len(containers)} containers')
```

**Note**: Concurrent execution includes built-in rate limiting, circuit breaker protection, and retry logic to ensure reliable API communication.

#### Enhanced Error Handling

The SDK includes comprehensive error handling and retry mechanisms:

```
# Automatic retry with exponential backoff
try:
    result = pc_api.hosts_list_read(concurrent=True, max_workers=3)
except Exception as e:
    print(f"Request failed: {e}")

# Built-in features:
# - Circuit breaker pattern (prevents cascading failures)
# - Rate limiting (respects API limits)
# - Exponential backoff retry logic
# - Authentication error recovery
# - Connection pooling and timeout handling
# - Progress tracking for large datasets
```

Settings can also be defined as environment variables:

#### Environment Variables

```
settings = {
    "url":      os.environ.get('PC_URL'),
    "identity": os.environ.get('PC_IDENTITY'),
    "secret":   os.environ.get('PC_SECRET')
}
```

## Support

This project has been developed by members of the Prisma Cloud CS and SE teams, it is not Supported by Palo Alto Networks.
Nevertheless, the maintainers will make a best-effort to address issues, and (of course) contributors are encouraged to submit issues and pull requests.
