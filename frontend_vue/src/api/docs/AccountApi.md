# Adherent.AccountApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**accountGet**](AccountApi.md#accountGet) | **GET** /account/ | Filter accounts
[**accountIdGet**](AccountApi.md#accountIdGet) | **GET** /account/{id} | Retrieve
[**accountIdPatch**](AccountApi.md#accountIdPatch) | **PATCH** /account/{id} | Partially update
[**accountPost**](AccountApi.md#accountPost) | **POST** /account/ | Create account



## accountGet

> [Account] accountGet(opts)

Filter accounts

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.AccountApi();
let opts = {
  'limit': 100, // Number | Limit the number of accounts returned in the result. Default is 100
  'offset': 0, // Number | Skip the first n results
  'terms': "terms_example", // String | The generic search terms (will search in any field)
  'name': "name_example", // String | Filter by name
  'type': 56 // Number | Filter by type
};
apiInstance.accountGet(opts).then((data) => {
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
 **type** | **Number**| Filter by type | [optional] 

### Return type

[**[Account]**](Account.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## accountIdGet

> Account accountIdGet(id)

Retrieve

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.AccountApi();
let id = 56; // Number | The id of the account that needs to be fetched.
apiInstance.accountIdGet(id).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Number**| The id of the account that needs to be fetched. | 

### Return type

[**Account**](Account.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## accountIdPatch

> accountIdPatch(id, accountPatchRequest)

Partially update

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.AccountApi();
let id = 56; // Number | id of the account will be updated
let accountPatchRequest = new Adherent.AccountPatchRequest(); // AccountPatchRequest | New values of the account
apiInstance.accountIdPatch(id, accountPatchRequest).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Number**| id of the account will be updated | 
 **accountPatchRequest** | [**AccountPatchRequest**](AccountPatchRequest.md)| New values of the account | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined


## accountPost

> accountPost(account)

Create account

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.AccountApi();
let account = new Adherent.Account(); // Account | New values of the account
apiInstance.accountPost(account).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account** | [**Account**](Account.md)| New values of the account | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined

