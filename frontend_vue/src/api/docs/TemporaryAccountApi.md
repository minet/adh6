# Adherent.TemporaryAccountApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**temporaryAccountDelete**](TemporaryAccountApi.md#temporaryAccountDelete) | **DELETE** /temporary_account/ | Revoke all active temporary accounts.
[**temporaryAccountPost**](TemporaryAccountApi.md#temporaryAccountPost) | **POST** /temporary_account/ | Create new temporary account for this day. Only super admins can do that.



## temporaryAccountDelete

> temporaryAccountDelete()

Revoke all active temporary accounts.

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.TemporaryAccountApi();
apiInstance.temporaryAccountDelete().then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters

This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


## temporaryAccountPost

> InlineResponse2001 temporaryAccountPost(inlineObject1)

Create new temporary account for this day. Only super admins can do that.

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.TemporaryAccountApi();
let inlineObject1 = new Adherent.InlineObject1(); // InlineObject1 | 
apiInstance.temporaryAccountPost(inlineObject1).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **inlineObject1** | [**InlineObject1**](InlineObject1.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

