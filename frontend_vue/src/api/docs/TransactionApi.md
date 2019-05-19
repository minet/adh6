# Adherent.TransactionApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**transactionGet**](TransactionApi.md#transactionGet) | **GET** /transaction/ | Filter transactions
[**transactionIdDelete**](TransactionApi.md#transactionIdDelete) | **DELETE** /transaction/{id} | Delete
[**transactionIdGet**](TransactionApi.md#transactionIdGet) | **GET** /transaction/{id} | Retrieve



## transactionGet

> [Transaction] transactionGet(opts)

Filter transactions

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.TransactionApi();
let opts = {
  'limit': 100, // Number | Limit the number of transactions returned in the result. Default is 100
  'offset': 0, // Number | Skip the first n results
  'terms': "terms_example", // String | The generic search terms (will search in any field)
  'account': 56 // Number | Filter by account id (either as source or destination)
};
apiInstance.transactionGet(opts).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Number**| Limit the number of transactions returned in the result. Default is 100 | [optional] [default to 100]
 **offset** | **Number**| Skip the first n results | [optional] [default to 0]
 **terms** | **String**| The generic search terms (will search in any field) | [optional] 
 **account** | **Number**| Filter by account id (either as source or destination) | [optional] 

### Return type

[**[Transaction]**](Transaction.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## transactionIdDelete

> transactionIdDelete(id)

Delete

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.TransactionApi();
let id = 56; // Number | The unique identifier of the transaction that will be deleted
apiInstance.transactionIdDelete(id).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Number**| The unique identifier of the transaction that will be deleted | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


## transactionIdGet

> Transaction transactionIdGet(id)

Retrieve

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.TransactionApi();
let id = 56; // Number | The unique identifier of the transaction that needs to be fetched
apiInstance.transactionIdGet(id).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Number**| The unique identifier of the transaction that needs to be fetched | 

### Return type

[**Transaction**](Transaction.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

