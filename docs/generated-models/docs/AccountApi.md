# adh6.AccountApi

All URIs are relative to *https://adh6.minet.net/api/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**account_get**](AccountApi.md#account_get) | **GET** /account/ | Filter accounts
[**account_id_get**](AccountApi.md#account_id_get) | **GET** /account/{id} | Retrieve an account
[**account_id_put**](AccountApi.md#account_id_put) | **PUT** /account/{id} | Udate an account
[**account_post**](AccountApi.md#account_post) | **POST** /account/ | Create an account
[**account_type_get**](AccountApi.md#account_type_get) | **GET** /account_type/ | Filter account types
[**account_type_id_get**](AccountApi.md#account_type_id_get) | **GET** /account_type/{id} | Retrieve an account type

# **account_get**
> list[AbstractAccount] account_get(limit=limit, offset=offset, terms=terms, filter=filter, only=only)

Filter accounts

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
api_instance = adh6.AccountApi(adh6.ApiClient(configuration))
limit = 25 # int | Limit the number of results returned (optional) (default to 25)
offset = 0 # int | Skip the first n results (optional) (default to 0)
terms = 'terms_example' # str | The generic search terms (will search in any field) (optional)
filter = NULL # object | Filters by various properties (optional)
only = ['only_example'] # list[str] | Limit to specific attributes (optional)

try:
    # Filter accounts
    api_response = api_instance.account_get(limit=limit, offset=offset, terms=terms, filter=filter, only=only)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AccountApi->account_get: %s\n" % e)
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

[**list[AbstractAccount]**](AbstractAccount.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **account_id_get**
> AbstractAccount account_id_get(id, only=only)

Retrieve an account

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
api_instance = adh6.AccountApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.
only = ['only_example'] # list[str] | Limit to specific attributes (optional)

try:
    # Retrieve an account
    api_response = api_instance.account_id_get(id, only=only)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AccountApi->account_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 
 **only** | [**list[str]**](str.md)| Limit to specific attributes | [optional] 

### Return type

[**AbstractAccount**](AbstractAccount.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **account_id_put**
> account_id_put(body, id)

Udate an account

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
api_instance = adh6.AccountApi(adh6.ApiClient(configuration))
body = adh6.AbstractAccount() # AbstractAccount | The new values for this account
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Udate an account
    api_instance.account_id_put(body, id)
except ApiException as e:
    print("Exception when calling AccountApi->account_id_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AbstractAccount**](AbstractAccount.md)| The new values for this account | 
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

void (empty response body)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **account_post**
> Account account_post(body)

Create an account

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
api_instance = adh6.AccountApi(adh6.ApiClient(configuration))
body = adh6.Account() # Account | The account to create

try:
    # Create an account
    api_response = api_instance.account_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AccountApi->account_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Account**](Account.md)| The account to create | 

### Return type

[**Account**](Account.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **account_type_get**
> list[AccountType] account_type_get(limit=limit, offset=offset, terms=terms)

Filter account types

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
api_instance = adh6.AccountApi(adh6.ApiClient(configuration))
limit = 25 # int | Limit the number of results returned (optional) (default to 25)
offset = 0 # int | Skip the first n results (optional) (default to 0)
terms = 'terms_example' # str | The generic search terms (will search in any field) (optional)

try:
    # Filter account types
    api_response = api_instance.account_type_get(limit=limit, offset=offset, terms=terms)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AccountApi->account_type_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Limit the number of results returned | [optional] [default to 25]
 **offset** | **int**| Skip the first n results | [optional] [default to 0]
 **terms** | **str**| The generic search terms (will search in any field) | [optional] 

### Return type

[**list[AccountType]**](AccountType.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **account_type_id_get**
> AccountType account_type_id_get(id)

Retrieve an account type

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
api_instance = adh6.AccountApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Retrieve an account type
    api_response = api_instance.account_type_id_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AccountApi->account_type_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

[**AccountType**](AccountType.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

