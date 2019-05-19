# Adherent.PortApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**mabGet**](PortApi.md#mabGet) | **GET** /port/{port_id}/mab/ | Check whether MAB is enable on this port or not.
[**portGet**](PortApi.md#portGet) | **GET** /port/ | Filter ports
[**portPortIdDelete**](PortApi.md#portPortIdDelete) | **DELETE** /port/{port_id} | Delete a port
[**portPortIdGet**](PortApi.md#portPortIdGet) | **GET** /port/{port_id} | Retrieve a port
[**portPortIdMabPut**](PortApi.md#portPortIdMabPut) | **PUT** /port/{port_id}/mab/ | Enable/disable MAB on a port
[**portPortIdPut**](PortApi.md#portPortIdPut) | **PUT** /port/{port_id} | Update a port
[**portPortIdStatePut**](PortApi.md#portPortIdStatePut) | **PUT** /port/{port_id}/state/ | Shutdown/enable a port
[**portPortIdVlanPut**](PortApi.md#portPortIdVlanPut) | **PUT** /port/{port_id}/vlan/ | Change the VLAN assigned a to port
[**portPost**](PortApi.md#portPost) | **POST** /port/ | Create a port
[**stateGet**](PortApi.md#stateGet) | **GET** /port/{port_id}/state/ | Retrieve the status of a port.
[**vlanGet**](PortApi.md#vlanGet) | **GET** /port/{port_id}/vlan/ | Retrieve the VLAN assigned to the port.



## mabGet

> Boolean mabGet(portId)

Check whether MAB is enable on this port or not.

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PortApi();
let portId = 56; // Number | 
apiInstance.mabGet(portId).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **portId** | **Number**|  | 

### Return type

**Boolean**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## portGet

> [Port] portGet(opts)

Filter ports

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PortApi();
let opts = {
  'limit': 100, // Number | Limit the number of ports returned in the result. Default is 100
  'offset': 0, // Number | Skip the first n results
  'switchID': 56, // Number | Filter only ports from that switch
  'roomNumber': 56, // Number | Filter only ports from that room
  'terms': "terms_example" // String | Search terms
};
apiInstance.portGet(opts).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Number**| Limit the number of ports returned in the result. Default is 100 | [optional] [default to 100]
 **offset** | **Number**| Skip the first n results | [optional] [default to 0]
 **switchID** | **Number**| Filter only ports from that switch | [optional] 
 **roomNumber** | **Number**| Filter only ports from that room | [optional] 
 **terms** | **String**| Search terms | [optional] 

### Return type

[**[Port]**](Port.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## portPortIdDelete

> portPortIdDelete(portId)

Delete a port

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PortApi();
let portId = 56; // Number | 
apiInstance.portPortIdDelete(portId).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **portId** | **Number**|  | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


## portPortIdGet

> Port portPortIdGet(portId)

Retrieve a port

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PortApi();
let portId = 56; // Number | 
apiInstance.portPortIdGet(portId).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **portId** | **Number**|  | 

### Return type

[**Port**](Port.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## portPortIdMabPut

> portPortIdMabPut(portId, body)

Enable/disable MAB on a port

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PortApi();
let portId = 56; // Number | 
let body = true; // Boolean | 
apiInstance.portPortIdMabPut(portId, body).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **portId** | **Number**|  | 
 **body** | **Boolean**|  | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined


## portPortIdPut

> portPortIdPut(portId, port)

Update a port

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PortApi();
let portId = 56; // Number | 
let port = new Adherent.Port(); // Port | Port to update
apiInstance.portPortIdPut(portId, port).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **portId** | **Number**|  | 
 **port** | [**Port**](Port.md)| Port to update | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined


## portPortIdStatePut

> portPortIdStatePut(portId, body)

Shutdown/enable a port

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PortApi();
let portId = 56; // Number | 
let body = true; // Boolean | True to open, False to shutdown
apiInstance.portPortIdStatePut(portId, body).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **portId** | **Number**|  | 
 **body** | **Boolean**| True to open, False to shutdown | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined


## portPortIdVlanPut

> portPortIdVlanPut(portId, body)

Change the VLAN assigned a to port

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PortApi();
let portId = 56; // Number | 
let body = 56; // Number | VLAN to assign. Set it to 1 if you want to enable authentication on the port.
apiInstance.portPortIdVlanPut(portId, body).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **portId** | **Number**|  | 
 **body** | **Number**| VLAN to assign. Set it to 1 if you want to enable authentication on the port. | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined


## portPost

> portPost(port)

Create a port

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PortApi();
let port = new Adherent.Port(); // Port | Port to create
apiInstance.portPost(port).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **port** | [**Port**](Port.md)| Port to create | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined


## stateGet

> Boolean stateGet(portId)

Retrieve the status of a port.

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PortApi();
let portId = 56; // Number | 
apiInstance.stateGet(portId).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **portId** | **Number**|  | 

### Return type

**Boolean**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## vlanGet

> Number vlanGet(portId)

Retrieve the VLAN assigned to the port.

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.PortApi();
let portId = 56; // Number | 
apiInstance.vlanGet(portId).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **portId** | **Number**|  | 

### Return type

**Number**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

