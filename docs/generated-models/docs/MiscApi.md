# adh6.MiscApi

All URIs are relative to *https://adh6.minet.net/api/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**health**](MiscApi.md#health) | **GET** /health | Retrieve the health of the API server
[**profile**](MiscApi.md#profile) | **GET** /profile | Introspection endpoint

# **health**
> health()

Retrieve the health of the API server

This endpoint allows for better monitoring of the state of the API. **TODO**: Improve the amount of information returned 

### Example
```python
from __future__ import print_function
import time
import adh6
from adh6.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = adh6.MiscApi()

try:
    # Retrieve the health of the API server
    api_instance.health()
except ApiException as e:
    print("Exception when calling MiscApi->health: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **profile**
> InlineResponse200 profile()

Introspection endpoint

This endpoint returns information about the currently logged-in user. 

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
api_instance = adh6.MiscApi(adh6.ApiClient(configuration))

try:
    # Introspection endpoint
    api_response = api_instance.profile()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MiscApi->profile: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

