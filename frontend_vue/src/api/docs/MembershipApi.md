# Adherent.MembershipApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**memberUsernameMembershipPost**](MembershipApi.md#memberUsernameMembershipPost) | **POST** /member/{username}/membership/ | Add a membership record for an member



## memberUsernameMembershipPost

> memberUsernameMembershipPost(username, membershipRequest, opts)

Add a membership record for an member

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.MembershipApi();
let username = "username_example"; // String | The username of the member
let membershipRequest = new Adherent.MembershipRequest(); // MembershipRequest | Membership record, if no start is specified, it will use the current date. Duration is expressed in days. WARNING: DO NOT set the start date to be in the future, it is not implemented for the moment.
let opts = {
  'xIdempotencyKey': "xIdempotencyKey_example" // String | Just a random string to ensure that membership creation is idempotent (very important since double submission may result to the member being charged two times). I recommand using a long random string for that.
};
apiInstance.memberUsernameMembershipPost(username, membershipRequest, opts).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **String**| The username of the member | 
 **membershipRequest** | [**MembershipRequest**](MembershipRequest.md)| Membership record, if no start is specified, it will use the current date. Duration is expressed in days. WARNING: DO NOT set the start date to be in the future, it is not implemented for the moment. | 
 **xIdempotencyKey** | **String**| Just a random string to ensure that membership creation is idempotent (very important since double submission may result to the member being charged two times). I recommand using a long random string for that. | [optional] 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined

