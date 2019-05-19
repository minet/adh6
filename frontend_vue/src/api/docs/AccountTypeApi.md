# Adherent.AccountTypeApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**accountTypeAccountTypeIdGet**](AccountTypeApi.md#accountTypeAccountTypeIdGet) | **GET** /account_type/{account_type_id} | Retrieve an account type
[**accountTypeAccountTypeIdPatch**](AccountTypeApi.md#accountTypeAccountTypeIdPatch) | **PATCH** /account_type/{account_type_id} | Partially update
[**accountTypeGet**](AccountTypeApi.md#accountTypeGet) | **GET** /account_type/ | Filter account types
[**accountTypePost**](AccountTypeApi.md#accountTypePost) | **POST** /account_type/ | Create an account type



## accountTypeAccountTypeIdGet

> AccountType accountTypeAccountTypeIdGet(accountTypeId)

Retrieve an account type

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.AccountTypeApi();
let accountTypeId = 56; // Number | 
apiInstance.accountTypeAccountTypeIdGet(accountTypeId).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **accountTypeId** | **Number**|  | 

### Return type

[**AccountType**](AccountType.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## accountTypeAccountTypeIdPatch

> accountTypeAccountTypeIdPatch(accountTypeId, accountTypePatchRequest)

Partially update

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.AccountTypeApi();
let accountTypeId = "accountTypeId_example"; // String | Name of the account type will be updated
let accountTypePatchRequest = new Adherent.AccountTypePatchRequest(); // AccountTypePatchRequest | New values of the account type
apiInstance.accountTypeAccountTypeIdPatch(accountTypeId, accountTypePatchRequest).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **accountTypeId** | **String**| Name of the account type will be updated | 
 **accountTypePatchRequest** | [**AccountTypePatchRequest**](AccountTypePatchRequest.md)| New values of the account type | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined


## accountTypeGet

> [AccountType] accountTypeGet(opts)

Filter account types

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.AccountTypeApi();
let opts = {
  'limit': 100, // Number | Limit the number of account types returned in the result. Default is 100
  'offset': 0, // Number | Skip the first n results
  'terms': "terms_example" // String | Search terms
};
apiInstance.accountTypeGet(opts).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Number**| Limit the number of account types returned in the result. Default is 100 | [optional] [default to 100]
 **offset** | **Number**| Skip the first n results | [optional] [default to 0]
 **terms** | **String**| Search terms | [optional] 

### Return type

[**[AccountType]**](AccountType.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## accountTypePost

> accountTypePost(accountType)

Create an account type

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.AccountTypeApi();
let accountType = new Adherent.AccountType(); // AccountType | Account type to create
apiInstance.accountTypePost(accountType).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **accountType** | [**AccountType**](AccountType.md)| Account type to create | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined

