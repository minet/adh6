# adh6.MembershipApi

All URIs are relative to *https://adh6.minet.net/api/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_latest_membership**](MembershipApi.md#get_latest_membership) | **GET** /member/{id}/membership/ | Get the latest pending membership of a specific member
[**member_id_membership_post**](MembershipApi.md#member_id_membership_post) | **POST** /member/{id}/membership/ | Add a membership record for a member
[**member_id_membership_uuid_patch**](MembershipApi.md#member_id_membership_uuid_patch) | **PATCH** /member/{id}/membership/{uuid} | Partially update a membership
[**membership_search**](MembershipApi.md#membership_search) | **GET** /member/membership/ | Filter memberships
[**membership_validate**](MembershipApi.md#membership_validate) | **GET** /member/{id}/membership/{uuid}/validate | Validate a pending transaction

# **get_latest_membership**
> AbstractMembership get_latest_membership(id, only=only)

Get the latest pending membership of a specific member

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
api_instance = adh6.MembershipApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.
only = ['only_example'] # list[str] | Limit to specific attributes (optional)

try:
    # Get the latest pending membership of a specific member
    api_response = api_instance.get_latest_membership(id, only=only)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MembershipApi->get_latest_membership: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 
 **only** | [**list[str]**](str.md)| Limit to specific attributes | [optional] 

### Return type

[**AbstractMembership**](AbstractMembership.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **member_id_membership_post**
> Membership member_id_membership_post(body, id)

Add a membership record for a member

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
api_instance = adh6.MembershipApi(adh6.ApiClient(configuration))
body = adh6.Membership() # Membership | The membership to create
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Add a membership record for a member
    api_response = api_instance.member_id_membership_post(body, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MembershipApi->member_id_membership_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Membership**](Membership.md)| The membership to create | 
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

[**Membership**](Membership.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **member_id_membership_uuid_patch**
> member_id_membership_uuid_patch(body, id, uuid)

Partially update a membership

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
api_instance = adh6.MembershipApi(adh6.ApiClient(configuration))
body = adh6.AbstractMembership() # AbstractMembership | The new values for this member
id = 56 # int | The id of the account that needs to be fetched.
uuid = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | The UUID associated with this membership request

try:
    # Partially update a membership
    api_instance.member_id_membership_uuid_patch(body, id, uuid)
except ApiException as e:
    print("Exception when calling MembershipApi->member_id_membership_uuid_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AbstractMembership**](AbstractMembership.md)| The new values for this member | 
 **id** | **int**| The id of the account that needs to be fetched. | 
 **uuid** | [**str**](.md)| The UUID associated with this membership request | 

### Return type

void (empty response body)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **membership_search**
> list[AbstractMembership] membership_search(limit=limit, offset=offset, terms=terms, filter=filter, only=only)

Filter memberships

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
api_instance = adh6.MembershipApi(adh6.ApiClient(configuration))
limit = 25 # int | Limit the number of results returned (optional) (default to 25)
offset = 0 # int | Skip the first n results (optional) (default to 0)
terms = 'terms_example' # str | The generic search terms (will search in any field) (optional)
filter = NULL # object | Filters by various properties (optional)
only = ['only_example'] # list[str] | Limit to specific attributes (optional)

try:
    # Filter memberships
    api_response = api_instance.membership_search(limit=limit, offset=offset, terms=terms, filter=filter, only=only)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MembershipApi->membership_search: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Limit the number of results returned | [optional] [default to 25]
 **offset** | **int**| Skip the first n results | [optional] [default to 0]
 **terms** | **str**| The generic search terms (will search in any field) | [optional] 
 **filter** | [**object**](.md)| Filters by various properties | [optional] 
 **only** | [**list[str]**](str.md)| Limit to specific attributes | [optional] 

### Return type

[**list[AbstractMembership]**](AbstractMembership.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **membership_validate**
> membership_validate(id, uuid, free=free)

Validate a pending transaction

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
api_instance = adh6.MembershipApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.
uuid = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | The UUID associated with this membership request
free = true # bool | Should the membership be free (optional)

try:
    # Validate a pending transaction
    api_instance.membership_validate(id, uuid, free=free)
except ApiException as e:
    print("Exception when calling MembershipApi->membership_validate: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 
 **uuid** | [**str**](.md)| The UUID associated with this membership request | 
 **free** | **bool**| Should the membership be free | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

