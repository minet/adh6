# adh6.VlanApi

All URIs are relative to *https://adh6.minet.net/api/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_from_number**](VlanApi.md#get_from_number) | **GET** /vlan/ | Filter vlans

# **get_from_number**
> AbstractVlan get_from_number(vlan_number, only=only)

Filter vlans

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
api_instance = adh6.VlanApi(adh6.ApiClient(configuration))
vlan_number = 56 # int | Number of the Vlan
only = ['only_example'] # list[str] | Limit to specific attributes (optional)

try:
    # Filter vlans
    api_response = api_instance.get_from_number(vlan_number, only=only)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VlanApi->get_from_number: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **vlan_number** | **int**| Number of the Vlan | 
 **only** | [**list[str]**](str.md)| Limit to specific attributes | [optional] 

### Return type

[**AbstractVlan**](AbstractVlan.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

