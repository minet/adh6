# adh6.MemberApi

All URIs are relative to *https://adh6.minet.net/api/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**charter_get**](MemberApi.md#charter_get) | **GET** /member/{id}/charter/{charter_id} | Retrieves if the hosting charter has been signed
[**charter_put**](MemberApi.md#charter_put) | **PUT** /member/{id}/charter/{charter_id} | Update if the hosting/MiNET charter has been signed
[**member_get**](MemberApi.md#member_get) | **GET** /member/ | Filter members
[**member_id_delete**](MemberApi.md#member_id_delete) | **DELETE** /member/{id} | Delete a member
[**member_id_get**](MemberApi.md#member_id_get) | **GET** /member/{id} | Retrieve a member
[**member_id_logs_get**](MemberApi.md#member_id_logs_get) | **GET** /member/{id}/logs/ | Retrieve the most recent logs of a member
[**member_id_password_put**](MemberApi.md#member_id_password_put) | **PUT** /member/{id}/password/ | Update the password of a member
[**member_id_patch**](MemberApi.md#member_id_patch) | **PATCH** /member/{id} | Partially update a member
[**member_id_put**](MemberApi.md#member_id_put) | **PUT** /member/{id} | Update a member
[**member_id_statuses_get**](MemberApi.md#member_id_statuses_get) | **GET** /member/{id}/statuses/ | Retrieves some common status updates concerning a member
[**member_post**](MemberApi.md#member_post) | **POST** /member/ | Create a member

# **charter_get**
> datetime charter_get(id, charter_id)

Retrieves if the hosting charter has been signed

### Example
```python
from __future__ import print_function
import time
import adh6
from adh6.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKeyAuth
configuration = adh6.Configuration()
configuration.api_key['X-API-KEY'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-KEY'] = 'Bearer'
# Configure OAuth2 access token for authorization: OAuth2
configuration = adh6.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = adh6.MemberApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.
charter_id = 56 # int | The unique identifier of the charter: 1 for MiNET and 2 for Hosting

try:
    # Retrieves if the hosting charter has been signed
    api_response = api_instance.charter_get(id, charter_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MemberApi->charter_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 
 **charter_id** | **int**| The unique identifier of the charter: 1 for MiNET and 2 for Hosting | 

### Return type

**datetime**

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **charter_put**
> charter_put(id, charter_id)

Update if the hosting/MiNET charter has been signed

### Example
```python
from __future__ import print_function
import time
import adh6
from adh6.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKeyAuth
configuration = adh6.Configuration()
configuration.api_key['X-API-KEY'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-KEY'] = 'Bearer'
# Configure OAuth2 access token for authorization: OAuth2
configuration = adh6.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = adh6.MemberApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.
charter_id = 56 # int | The unique identifier of the charter: 1 for MiNET and 2 for Hosting

try:
    # Update if the hosting/MiNET charter has been signed
    api_instance.charter_put(id, charter_id)
except ApiException as e:
    print("Exception when calling MemberApi->charter_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 
 **charter_id** | **int**| The unique identifier of the charter: 1 for MiNET and 2 for Hosting | 

### Return type

void (empty response body)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **member_get**
> list[AbstractMember] member_get(limit=limit, offset=offset, terms=terms, filter=filter, only=only, since=since, until=until, mailinglist=mailinglist)

Filter members

### Example
```python
from __future__ import print_function
import time
import adh6
from adh6.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKeyAuth
configuration = adh6.Configuration()
configuration.api_key['X-API-KEY'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-KEY'] = 'Bearer'
# Configure OAuth2 access token for authorization: OAuth2
configuration = adh6.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = adh6.MemberApi(adh6.ApiClient(configuration))
limit = 25 # int | Limit the number of results returned (optional) (default to 25)
offset = 0 # int | Skip the first n results (optional) (default to 0)
terms = 'terms_example' # str | The generic search terms (will search in any field) (optional)
filter = NULL # object | Filters by various properties (optional)
only = ['only_example'] # list[str] | Limit to specific attributes (optional)
since = '2013-10-20T19:20:30+01:00' # datetime | Filter member that have departureDate after (optional)
until = '2013-10-20T19:20:30+01:00' # datetime | Filter member that have departureDate before (optional)
mailinglist = 56 # int | Filter member by its membership in a specific mailing list (optional)

try:
    # Filter members
    api_response = api_instance.member_get(limit=limit, offset=offset, terms=terms, filter=filter, only=only, since=since, until=until, mailinglist=mailinglist)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MemberApi->member_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Limit the number of results returned | [optional] [default to 25]
 **offset** | **int**| Skip the first n results | [optional] [default to 0]
 **terms** | **str**| The generic search terms (will search in any field) | [optional] 
 **filter** | [**object**](.md)| Filters by various properties | [optional] 
 **only** | [**list[str]**](str.md)| Limit to specific attributes | [optional] 
 **since** | **datetime**| Filter member that have departureDate after | [optional] 
 **until** | **datetime**| Filter member that have departureDate before | [optional] 
 **mailinglist** | **int**| Filter member by its membership in a specific mailing list | [optional] 

### Return type

[**list[AbstractMember]**](AbstractMember.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **member_id_delete**
> member_id_delete(id)

Delete a member

### Example
```python
from __future__ import print_function
import time
import adh6
from adh6.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKeyAuth
configuration = adh6.Configuration()
configuration.api_key['X-API-KEY'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-KEY'] = 'Bearer'
# Configure OAuth2 access token for authorization: OAuth2
configuration = adh6.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = adh6.MemberApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Delete a member
    api_instance.member_id_delete(id)
except ApiException as e:
    print("Exception when calling MemberApi->member_id_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

void (empty response body)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **member_id_get**
> AbstractMember member_id_get(id, only=only)

Retrieve a member

### Example
```python
from __future__ import print_function
import time
import adh6
from adh6.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKeyAuth
configuration = adh6.Configuration()
configuration.api_key['X-API-KEY'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-KEY'] = 'Bearer'
# Configure OAuth2 access token for authorization: OAuth2
configuration = adh6.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = adh6.MemberApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.
only = ['only_example'] # list[str] | Limit to specific attributes (optional)

try:
    # Retrieve a member
    api_response = api_instance.member_id_get(id, only=only)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MemberApi->member_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 
 **only** | [**list[str]**](str.md)| Limit to specific attributes | [optional] 

### Return type

[**AbstractMember**](AbstractMember.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **member_id_logs_get**
> list[str] member_id_logs_get(id, dhcp=dhcp)

Retrieve the most recent logs of a member

### Example
```python
from __future__ import print_function
import time
import adh6
from adh6.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = adh6.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = adh6.MemberApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.
dhcp = true # bool | Whether to fetch DHCP logs (optional)

try:
    # Retrieve the most recent logs of a member
    api_response = api_instance.member_id_logs_get(id, dhcp=dhcp)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MemberApi->member_id_logs_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 
 **dhcp** | **bool**| Whether to fetch DHCP logs | [optional] 

### Return type

**list[str]**

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **member_id_password_put**
> member_id_password_put(body, id)

Update the password of a member

### Example
```python
from __future__ import print_function
import time
import adh6
from adh6.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = adh6.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = adh6.MemberApi(adh6.ApiClient(configuration))
body = adh6.Body() # Body | The new value for the password, either in plaintext or pre-hashed client-side
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Update the password of a member
    api_instance.member_id_password_put(body, id)
except ApiException as e:
    print("Exception when calling MemberApi->member_id_password_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Body**](Body.md)| The new value for the password, either in plaintext or pre-hashed client-side | 
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **member_id_patch**
> member_id_patch(body, id)

Partially update a member

### Example
```python
from __future__ import print_function
import time
import adh6
from adh6.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKeyAuth
configuration = adh6.Configuration()
configuration.api_key['X-API-KEY'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-KEY'] = 'Bearer'
# Configure OAuth2 access token for authorization: OAuth2
configuration = adh6.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = adh6.MemberApi(adh6.ApiClient(configuration))
body = adh6.AbstractMember() # AbstractMember | The new values for this member
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Partially update a member
    api_instance.member_id_patch(body, id)
except ApiException as e:
    print("Exception when calling MemberApi->member_id_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AbstractMember**](AbstractMember.md)| The new values for this member | 
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

void (empty response body)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **member_id_put**
> member_id_put(body, id)

Update a member

### Example
```python
from __future__ import print_function
import time
import adh6
from adh6.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKeyAuth
configuration = adh6.Configuration()
configuration.api_key['X-API-KEY'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-KEY'] = 'Bearer'
# Configure OAuth2 access token for authorization: OAuth2
configuration = adh6.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = adh6.MemberApi(adh6.ApiClient(configuration))
body = adh6.Member() # Member | The new values for this member
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Update a member
    api_instance.member_id_put(body, id)
except ApiException as e:
    print("Exception when calling MemberApi->member_id_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Member**](Member.md)| The new values for this member | 
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

void (empty response body)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **member_id_statuses_get**
> list[MemberStatus] member_id_statuses_get(id)

Retrieves some common status updates concerning a member

### Example
```python
from __future__ import print_function
import time
import adh6
from adh6.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKeyAuth
configuration = adh6.Configuration()
configuration.api_key['X-API-KEY'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-KEY'] = 'Bearer'
# Configure OAuth2 access token for authorization: OAuth2
configuration = adh6.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = adh6.MemberApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Retrieves some common status updates concerning a member
    api_response = api_instance.member_id_statuses_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MemberApi->member_id_statuses_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

[**list[MemberStatus]**](MemberStatus.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **member_post**
> Member member_post(body)

Create a member

### Example
```python
from __future__ import print_function
import time
import adh6
from adh6.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKeyAuth
configuration = adh6.Configuration()
configuration.api_key['X-API-KEY'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-API-KEY'] = 'Bearer'
# Configure OAuth2 access token for authorization: OAuth2
configuration = adh6.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = adh6.MemberApi(adh6.ApiClient(configuration))
body = adh6.Member() # Member | The member to create

try:
    # Create a member
    api_response = api_instance.member_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MemberApi->member_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Member**](Member.md)| The member to create | 

### Return type

[**Member**](Member.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

