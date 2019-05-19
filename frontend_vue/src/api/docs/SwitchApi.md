# Adherent.SwitchApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**switchGet**](SwitchApi.md#switchGet) | **GET** /switch/ | Get all switches
[**switchPost**](SwitchApi.md#switchPost) | **POST** /switch/ | Create a switch
[**switchSwitchIDDelete**](SwitchApi.md#switchSwitchIDDelete) | **DELETE** /switch/{switchID} | Delete a switch
[**switchSwitchIDGet**](SwitchApi.md#switchSwitchIDGet) | **GET** /switch/{switchID} | Retrieve a switch
[**switchSwitchIDPut**](SwitchApi.md#switchSwitchIDPut) | **PUT** /switch/{switchID} | Update a switch



## switchGet

> [ModelSwitch] switchGet(opts)

Get all switches

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.SwitchApi();
let opts = {
  'limit': 100, // Number | Limit the number of switches returned in the result. Default is 100
  'offset': 0, // Number | Skip the first n results
  'terms': "terms_example" // String | Search terms
};
apiInstance.switchGet(opts).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Number**| Limit the number of switches returned in the result. Default is 100 | [optional] [default to 100]
 **offset** | **Number**| Skip the first n results | [optional] [default to 0]
 **terms** | **String**| Search terms | [optional] 

### Return type

[**[ModelSwitch]**](ModelSwitch.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## switchPost

> switchPost(modelSwitch)

Create a switch

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.SwitchApi();
let modelSwitch = new Adherent.ModelSwitch(); // ModelSwitch | Switch to create
apiInstance.switchPost(modelSwitch).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **modelSwitch** | [**ModelSwitch**](ModelSwitch.md)| Switch to create | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined


## switchSwitchIDDelete

> switchSwitchIDDelete(switchID)

Delete a switch

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.SwitchApi();
let switchID = 56; // Number | 
apiInstance.switchSwitchIDDelete(switchID).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **switchID** | **Number**|  | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


## switchSwitchIDGet

> ModelSwitch switchSwitchIDGet(switchID)

Retrieve a switch

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.SwitchApi();
let switchID = 56; // Number | 
apiInstance.switchSwitchIDGet(switchID).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **switchID** | **Number**|  | 

### Return type

[**ModelSwitch**](ModelSwitch.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## switchSwitchIDPut

> switchSwitchIDPut(switchID, modelSwitch)

Update a switch

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.SwitchApi();
let switchID = 56; // Number | 
let modelSwitch = new Adherent.ModelSwitch(); // ModelSwitch | Switch to update
apiInstance.switchSwitchIDPut(switchID, modelSwitch).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **switchID** | **Number**|  | 
 **modelSwitch** | [**ModelSwitch**](ModelSwitch.md)| Switch to update | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined

