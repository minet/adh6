# Adherent.PaymentMethodApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**paymentMethodGet**](PaymentMethodApi.md#paymentMethodGet) | **GET** /payment_method/ | Filter payment methods
[**paymentMethodPaymentMethodIdGet**](PaymentMethodApi.md#paymentMethodPaymentMethodIdGet) | **GET** /payment_method/{payment_method_id} | Retrieve a payment method
[**paymentMethodPaymentMethodIdPatch**](PaymentMethodApi.md#paymentMethodPaymentMethodIdPatch) | **PATCH** /payment_method/{payment_method_id} | Partially update
[**paymentMethodPost**](PaymentMethodApi.md#paymentMethodPost) | **POST** /payment_method/ | Create a payment method



## paymentMethodGet

> [PaymentMethod] paymentMethodGet(opts)

Filter payment methods

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PaymentMethodApi();
let opts = {
  'limit': 100, // Number | Limit the number of payment methods returned in the result. Default is 100
  'offset': 0, // Number | Skip the first n results
  'terms': "terms_example" // String | Search terms
};
apiInstance.paymentMethodGet(opts).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Number**| Limit the number of payment methods returned in the result. Default is 100 | [optional] [default to 100]
 **offset** | **Number**| Skip the first n results | [optional] [default to 0]
 **terms** | **String**| Search terms | [optional] 

### Return type

[**[PaymentMethod]**](PaymentMethod.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## paymentMethodPaymentMethodIdGet

> PaymentMethod paymentMethodPaymentMethodIdGet(paymentMethodId)

Retrieve a payment method

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PaymentMethodApi();
let paymentMethodId = 56; // Number | 
apiInstance.paymentMethodPaymentMethodIdGet(paymentMethodId).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **paymentMethodId** | **Number**|  | 

### Return type

[**PaymentMethod**](PaymentMethod.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## paymentMethodPaymentMethodIdPatch

> paymentMethodPaymentMethodIdPatch(paymentMethodId, paymentMethodPatchRequest)

Partially update

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PaymentMethodApi();
let paymentMethodId = "paymentMethodId_example"; // String | Name of the payment method will be updated
let paymentMethodPatchRequest = new Adherent.PaymentMethodPatchRequest(); // PaymentMethodPatchRequest | New values of the payment method
apiInstance.paymentMethodPaymentMethodIdPatch(paymentMethodId, paymentMethodPatchRequest).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **paymentMethodId** | **String**| Name of the payment method will be updated | 
 **paymentMethodPatchRequest** | [**PaymentMethodPatchRequest**](PaymentMethodPatchRequest.md)| New values of the payment method | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined


## paymentMethodPost

> paymentMethodPost(paymentMethod)

Create a payment method

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PaymentMethodApi();
let paymentMethod = new Adherent.PaymentMethod(); // PaymentMethod | Payment method to create
apiInstance.paymentMethodPost(paymentMethod).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **paymentMethod** | [**PaymentMethod**](PaymentMethod.md)| Payment method to create | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined

