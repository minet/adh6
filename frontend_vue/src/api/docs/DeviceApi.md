# Adherent.DeviceApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**deviceGet**](DeviceApi.md#deviceGet) | **GET** /device/ | Filter devices
[**deviceMacAddressDelete**](DeviceApi.md#deviceMacAddressDelete) | **DELETE** /device/{mac_address} | Delete a device
[**deviceMacAddressGet**](DeviceApi.md#deviceMacAddressGet) | **GET** /device/{mac_address} | Retrieve a device
[**deviceMacAddressPut**](DeviceApi.md#deviceMacAddressPut) | **PUT** /device/{mac_address} | Update/create a device
[**vendorGet**](DeviceApi.md#vendorGet) | **GET** /device/{mac_address}/vendor | Retrieve the vendor of a device based on its MAC



## deviceGet

> [Device] deviceGet(opts)

Filter devices

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.DeviceApi();
let opts = {
  'limit': 100, // Number | Limit the number of devices returned in the result. Default is 100
  'offset': 0, // Number | Skip the first n results
  'username': "username_example", // String | Filter by owner's username
  'terms': "terms_example" // String | Search terms
};
apiInstance.deviceGet(opts).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Number**| Limit the number of devices returned in the result. Default is 100 | [optional] [default to 100]
 **offset** | **Number**| Skip the first n results | [optional] [default to 0]
 **username** | **String**| Filter by owner&#39;s username | [optional] 
 **terms** | **String**| Search terms | [optional] 

### Return type

[**[Device]**](Device.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## deviceMacAddressDelete

> deviceMacAddressDelete(macAddress)

Delete a device

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.DeviceApi();
let macAddress = "macAddress_example"; // String | The mac address of the device that will be deleted
apiInstance.deviceMacAddressDelete(macAddress).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **macAddress** | **String**| The mac address of the device that will be deleted | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


## deviceMacAddressGet

> Device deviceMacAddressGet(macAddress)

Retrieve a device

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.DeviceApi();
let macAddress = "macAddress_example"; // String | The mac address of the device that will be fetched
apiInstance.deviceMacAddressGet(macAddress).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **macAddress** | **String**| The mac address of the device that will be fetched | 

### Return type

[**Device**](Device.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## deviceMacAddressPut

> deviceMacAddressPut(macAddress, device)

Update/create a device

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.DeviceApi();
let macAddress = "macAddress_example"; // String | The mac address of the device that will be update
let device = new Adherent.Device(); // Device | Device to update
apiInstance.deviceMacAddressPut(macAddress, device).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **macAddress** | **String**| The mac address of the device that will be update | 
 **device** | [**Device**](Device.md)| Device to update | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined


## vendorGet

> InlineResponse200 vendorGet(macAddress)

Retrieve the vendor of a device based on its MAC

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.DeviceApi();
let macAddress = "macAddress_example"; // String | The mac address of the device that will be looked up
apiInstance.vendorGet(macAddress).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **macAddress** | **String**| The mac address of the device that will be looked up | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

