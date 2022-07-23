# adh6.AuthenticationApi

All URIs are relative to *https://adh6.minet.net/api/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_keys_get**](AuthenticationApi.md#api_keys_get) | **GET** /api_keys/ | List api keys
[**api_keys_id_delete**](AuthenticationApi.md#api_keys_id_delete) | **DELETE** /api_keys/{id} | Delete an Api Key
[**api_keys_post**](AuthenticationApi.md#api_keys_post) | **POST** /api_keys/ | Create an ApiKey
[**role_get**](AuthenticationApi.md#role_get) | **GET** /role/ | Filter roles
[**role_post**](AuthenticationApi.md#role_post) | **POST** /role/ | Create a temporary role for a user

# **api_keys_get**
> list[ApiKey] api_keys_get(limit=limit, offset=offset, login=login)

List api keys

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
api_instance = adh6.AuthenticationApi(adh6.ApiClient(configuration))
limit = 25 # int | Limit the number of results returned (optional) (default to 25)
offset = 0 # int | Skip the first n results (optional) (default to 0)
login = 'login_example' # str | The login of the user (optional)

try:
    # List api keys
    api_response = api_instance.api_keys_get(limit=limit, offset=offset, login=login)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->api_keys_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Limit the number of results returned | [optional] [default to 25]
 **offset** | **int**| Skip the first n results | [optional] [default to 0]
 **login** | **str**| The login of the user | [optional] 

### Return type

[**list[ApiKey]**](ApiKey.md)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_keys_id_delete**
> api_keys_id_delete(id)

Delete an Api Key

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
api_instance = adh6.AuthenticationApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Delete an Api Key
    api_instance.api_keys_id_delete(id)
except ApiException as e:
    print("Exception when calling AuthenticationApi->api_keys_id_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_keys_post**
> str api_keys_post(body)

Create an ApiKey

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
api_instance = adh6.AuthenticationApi(adh6.ApiClient(configuration))
body = adh6.Body2() # Body2 | The room to create

try:
    # Create an ApiKey
    api_response = api_instance.api_keys_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->api_keys_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Body2**](Body2.md)| The room to create | 

### Return type

**str**

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **role_get**
> list[Role] role_get(filter)

Filter roles

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
api_instance = adh6.AuthenticationApi(adh6.ApiClient(configuration))
filter = NULL # object | Filters by various properties

try:
    # Filter roles
    api_response = api_instance.role_get(filter)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->role_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | [**object**](.md)| Filters by various properties | 

### Return type

[**list[Role]**](Role.md)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **role_post**
> role_post(body)

Create a temporary role for a user

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
api_instance = adh6.AuthenticationApi(adh6.ApiClient(configuration))
body = adh6.Body1() # Body1 | The role to create

try:
    # Create a temporary role for a user
    api_instance.role_post(body)
except ApiException as e:
    print("Exception when calling AuthenticationApi->role_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Body1**](Body1.md)| The role to create | 

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

