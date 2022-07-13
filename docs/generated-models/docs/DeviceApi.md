# adh6.DeviceApi

All URIs are relative to *https://adh6.minet.net/api/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**device_get**](DeviceApi.md#device_get) | **GET** /device/ | Filter devices
[**device_id_delete**](DeviceApi.md#device_id_delete) | **DELETE** /device/{id} | Delete a device
[**device_id_get**](DeviceApi.md#device_id_get) | **GET** /device/{id} | Retrieve a device
[**device_id_patch**](DeviceApi.md#device_id_patch) | **PATCH** /device/{id} | Partially update a device
[**device_id_put**](DeviceApi.md#device_id_put) | **PUT** /device/{id} | Update a device
[**device_mab_get**](DeviceApi.md#device_mab_get) | **GET** /device/{id}/mab/ | Retrieve the vendor of a device based on its MAC
[**device_mab_put**](DeviceApi.md#device_mab_put) | **PUT** /device/{id}/mab/ | Retrieve the vendor of a device based on its MAC
[**device_post**](DeviceApi.md#device_post) | **POST** /device/ | Create device
[**vendor_get**](DeviceApi.md#vendor_get) | **GET** /device/{id}/vendor | Retrieve the vendor of a device based on its MAC

# **device_get**
> list[AbstractDevice] device_get(limit=limit, offset=offset, terms=terms, filter=filter, only=only)

Filter devices

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
api_instance = adh6.DeviceApi(adh6.ApiClient(configuration))
limit = 25 # int | Limit the number of results returned (optional) (default to 25)
offset = 0 # int | Skip the first n results (optional) (default to 0)
terms = 'terms_example' # str | The generic search terms (will search in any field) (optional)
filter = NULL # object | Filters by various properties (optional)
only = ['only_example'] # list[str] | Limit to specific attributes (optional)

try:
    # Filter devices
    api_response = api_instance.device_get(limit=limit, offset=offset, terms=terms, filter=filter, only=only)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeviceApi->device_get: %s\n" % e)
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

[**list[AbstractDevice]**](AbstractDevice.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **device_id_delete**
> device_id_delete(id)

Delete a device

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
api_instance = adh6.DeviceApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Delete a device
    api_instance.device_id_delete(id)
except ApiException as e:
    print("Exception when calling DeviceApi->device_id_delete: %s\n" % e)
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

# **device_id_get**
> Device device_id_get(id)

Retrieve a device

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
api_instance = adh6.DeviceApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Retrieve a device
    api_response = api_instance.device_id_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeviceApi->device_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

[**Device**](Device.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **device_id_patch**
> device_id_patch(body, id)

Partially update a device

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
api_instance = adh6.DeviceApi(adh6.ApiClient(configuration))
body = adh6.AbstractDevice() # AbstractDevice | The new values for this Device
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Partially update a device
    api_instance.device_id_patch(body, id)
except ApiException as e:
    print("Exception when calling DeviceApi->device_id_patch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AbstractDevice**](AbstractDevice.md)| The new values for this Device | 
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

void (empty response body)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **device_id_put**
> Device device_id_put(body, id)

Update a device

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
api_instance = adh6.DeviceApi(adh6.ApiClient(configuration))
body = adh6.AbstractDevice() # AbstractDevice | The new values for this device
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Update a device
    api_response = api_instance.device_id_put(body, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeviceApi->device_id_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AbstractDevice**](AbstractDevice.md)| The new values for this device | 
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

[**Device**](Device.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **device_mab_get**
> bool device_mab_get(id)

Retrieve the vendor of a device based on its MAC

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
api_instance = adh6.DeviceApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Retrieve the vendor of a device based on its MAC
    api_response = api_instance.device_mab_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeviceApi->device_mab_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

**bool**

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **device_mab_put**
> bool device_mab_put(id)

Retrieve the vendor of a device based on its MAC

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
api_instance = adh6.DeviceApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Retrieve the vendor of a device based on its MAC
    api_response = api_instance.device_mab_put(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeviceApi->device_mab_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

**bool**

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **device_post**
> Device device_post(body)

Create device

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
api_instance = adh6.DeviceApi(adh6.ApiClient(configuration))
body = adh6.Device() # Device | The device to create

try:
    # Create device
    api_response = api_instance.device_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeviceApi->device_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Device**](Device.md)| The device to create | 

### Return type

[**Device**](Device.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **vendor_get**
> Vendor vendor_get(id)

Retrieve the vendor of a device based on its MAC

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
api_instance = adh6.DeviceApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Retrieve the vendor of a device based on its MAC
    api_response = api_instance.vendor_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeviceApi->vendor_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

[**Vendor**](Vendor.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

