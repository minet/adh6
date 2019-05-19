# Adherent.ProductApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**productGet**](ProductApi.md#productGet) | **GET** /product/ | Filter products
[**productIdGet**](ProductApi.md#productIdGet) | **GET** /product/{id} | Retrieve
[**productPost**](ProductApi.md#productPost) | **POST** /product/ | Create product



## productGet

> [Product] productGet(opts)

Filter products

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.ProductApi();
let opts = {
  'limit': 100, // Number | Limit the number of accounts returned in the result. Default is 100
  'offset': 0, // Number | Skip the first n results
  'terms': "terms_example", // String | The generic search terms (will search in any field)
  'name': "name_example" // String | Filter by name
};
apiInstance.productGet(opts).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Number**| Limit the number of accounts returned in the result. Default is 100 | [optional] [default to 100]
 **offset** | **Number**| Skip the first n results | [optional] [default to 0]
 **terms** | **String**| The generic search terms (will search in any field) | [optional] 
 **name** | **String**| Filter by name | [optional] 

### Return type

[**[Product]**](Product.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## productIdGet

> Product productIdGet(id)

Retrieve

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.ProductApi();
let id = 56; // Number | The id of the product that needs to be fetched.
apiInstance.productIdGet(id).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Number**| The id of the product that needs to be fetched. | 

### Return type

[**Product**](Product.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## productPost

> productPost(product)

Create product

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.ProductApi();
let product = new Adherent.Product(); // Product | New values of the product
apiInstance.productPost(product).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **product** | [**Product**](Product.md)| New values of the product | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined

