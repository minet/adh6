# adh6.TreasuryApi

All URIs are relative to *https://adh6.minet.net/api/*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_bank**](TreasuryApi.md#get_bank) | **GET** /treasury/bank | Retrieve the expected state of MiNET&#x27;s bank accounts
[**get_cashbox**](TreasuryApi.md#get_cashbox) | **GET** /treasury/cashbox | Retrieve the state of the cashbox
[**product_buy_post**](TreasuryApi.md#product_buy_post) | **POST** /product/buy | Generate a new transaction for a product
[**product_get**](TreasuryApi.md#product_get) | **GET** /product/ | Filter products
[**product_id_get**](TreasuryApi.md#product_id_get) | **GET** /product/{id} | Retrieve a product

# **get_bank**
> Bank get_bank()

Retrieve the expected state of MiNET's bank accounts

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
api_instance = adh6.TreasuryApi(adh6.ApiClient(configuration))

try:
    # Retrieve the expected state of MiNET's bank accounts
    api_response = api_instance.get_bank()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TreasuryApi->get_bank: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Bank**](Bank.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cashbox**
> Cashbox get_cashbox()

Retrieve the state of the cashbox

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
api_instance = adh6.TreasuryApi(adh6.ApiClient(configuration))

try:
    # Retrieve the state of the cashbox
    api_response = api_instance.get_cashbox()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TreasuryApi->get_cashbox: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Cashbox**](Cashbox.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **product_buy_post**
> product_buy_post(member_id, products, payment_method)

Generate a new transaction for a product

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
api_instance = adh6.TreasuryApi(adh6.ApiClient(configuration))
member_id = 56 # int | Member that buy th products
products = [56] # list[int] | List of the products to add in the transaction
payment_method = 56 # int | Payment Method used to buy the products

try:
    # Generate a new transaction for a product
    api_instance.product_buy_post(member_id, products, payment_method)
except ApiException as e:
    print("Exception when calling TreasuryApi->product_buy_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **member_id** | **int**| Member that buy th products | 
 **products** | [**list[int]**](int.md)| List of the products to add in the transaction | 
 **payment_method** | **int**| Payment Method used to buy the products | 

### Return type

void (empty response body)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **product_get**
> list[Product] product_get(limit=limit, offset=offset, terms=terms)

Filter products

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
api_instance = adh6.TreasuryApi(adh6.ApiClient(configuration))
limit = 25 # int | Limit the number of results returned (optional) (default to 25)
offset = 0 # int | Skip the first n results (optional) (default to 0)
terms = 'terms_example' # str | The generic search terms (will search in any field) (optional)

try:
    # Filter products
    api_response = api_instance.product_get(limit=limit, offset=offset, terms=terms)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TreasuryApi->product_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Limit the number of results returned | [optional] [default to 25]
 **offset** | **int**| Skip the first n results | [optional] [default to 0]
 **terms** | **str**| The generic search terms (will search in any field) | [optional] 

### Return type

[**list[Product]**](Product.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **product_id_get**
> Product product_id_get(id)

Retrieve a product

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
api_instance = adh6.TreasuryApi(adh6.ApiClient(configuration))
id = 56 # int | The id of the account that needs to be fetched.

try:
    # Retrieve a product
    api_response = api_instance.product_id_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TreasuryApi->product_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The id of the account that needs to be fetched. | 

### Return type

[**Product**](Product.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

