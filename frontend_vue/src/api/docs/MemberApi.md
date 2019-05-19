# Adherent.MemberApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**memberGet**](MemberApi.md#memberGet) | **GET** /member/ | Filter members
[**memberUsernameDelete**](MemberApi.md#memberUsernameDelete) | **DELETE** /member/{username} | Delete
[**memberUsernameGet**](MemberApi.md#memberUsernameGet) | **GET** /member/{username} | Retrieve
[**memberUsernameLogsGet**](MemberApi.md#memberUsernameLogsGet) | **GET** /member/{username}/logs/ | Get the most recent logs
[**memberUsernamePasswordPut**](MemberApi.md#memberUsernamePasswordPut) | **PUT** /member/{username}/password/ | Update password
[**memberUsernamePatch**](MemberApi.md#memberUsernamePatch) | **PATCH** /member/{username} | Partially update
[**memberUsernamePut**](MemberApi.md#memberUsernamePut) | **PUT** /member/{username} | Update/create



## memberGet

> [Member] memberGet(opts)

Filter members

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.MemberApi();
let opts = {
  'limit': 100, // Number | Limit the number of members returned in the result. Default is 100
  'offset': 0, // Number | Skip the first n results
  'terms': "terms_example", // String | The generic search terms (will search in any field)
  'roomNumber': 56 // Number | Filter by room number
};
apiInstance.memberGet(opts).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Number**| Limit the number of members returned in the result. Default is 100 | [optional] [default to 100]
 **offset** | **Number**| Skip the first n results | [optional] [default to 0]
 **terms** | **String**| The generic search terms (will search in any field) | [optional] 
 **roomNumber** | **Number**| Filter by room number | [optional] 

### Return type

[**[Member]**](Member.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## memberUsernameDelete

> memberUsernameDelete(username)

Delete

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.MemberApi();
let username = "username_example"; // String | The username of the member that will be deleted
apiInstance.memberUsernameDelete(username).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **String**| The username of the member that will be deleted | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


## memberUsernameGet

> Member memberUsernameGet(username)

Retrieve

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.MemberApi();
let username = "username_example"; // String | The username of the member that needs to be fetched.
apiInstance.memberUsernameGet(username).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **String**| The username of the member that needs to be fetched. | 

### Return type

[**Member**](Member.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## memberUsernameLogsGet

> [String] memberUsernameLogsGet(username)

Get the most recent logs

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.MemberApi();
let username = "username_example"; // String | username of the member
apiInstance.memberUsernameLogsGet(username).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **String**| username of the member | 

### Return type

**[String]**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## memberUsernamePasswordPut

> memberUsernamePasswordPut(username, inlineObject)

Update password

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.MemberApi();
let username = "username_example"; // String | username of the member will be updated
let inlineObject = new Adherent.InlineObject(); // InlineObject | 
apiInstance.memberUsernamePasswordPut(username, inlineObject).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **String**| username of the member will be updated | 
 **inlineObject** | [**InlineObject**](InlineObject.md)|  | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined


## memberUsernamePatch

> memberUsernamePatch(username, memberPatchRequest)

Partially update

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.MemberApi();
let username = "username_example"; // String | username of the member will be updated
let memberPatchRequest = new Adherent.MemberPatchRequest(); // MemberPatchRequest | New values of the member
apiInstance.memberUsernamePatch(username, memberPatchRequest).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **String**| username of the member will be updated | 
 **memberPatchRequest** | [**MemberPatchRequest**](MemberPatchRequest.md)| New values of the member | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined


## memberUsernamePut

> memberUsernamePut(username, member)

Update/create

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.MemberApi();
let username = "username_example"; // String | username of the member will be updated
let member = new Adherent.Member(); // Member | New values of the member
apiInstance.memberUsernamePut(username, member).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **String**| username of the member will be updated | 
 **member** | [**Member**](Member.md)| New values of the member | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined

