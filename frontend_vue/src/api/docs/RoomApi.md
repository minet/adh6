# Adherent.RoomApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**roomGet**](RoomApi.md#roomGet) | **GET** /room/ | Filter rooms
[**roomRoomNumberDelete**](RoomApi.md#roomRoomNumberDelete) | **DELETE** /room/{roomNumber} | Delete a room
[**roomRoomNumberGet**](RoomApi.md#roomRoomNumberGet) | **GET** /room/{roomNumber} | Retrieve a room
[**roomRoomNumberPut**](RoomApi.md#roomRoomNumberPut) | **PUT** /room/{roomNumber} | Update/create a room



## roomGet

> [Room] roomGet(opts)

Filter rooms

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.RoomApi();
let opts = {
  'limit': 100, // Number | Limit the number of rooms returned in the result. Default is 100
  'offset': 0, // Number | Skip the first n results
  'terms': "terms_example" // String | Search terms
};
apiInstance.roomGet(opts).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Number**| Limit the number of rooms returned in the result. Default is 100 | [optional] [default to 100]
 **offset** | **Number**| Skip the first n results | [optional] [default to 0]
 **terms** | **String**| Search terms | [optional] 

### Return type

[**[Room]**](Room.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## roomRoomNumberDelete

> roomRoomNumberDelete(roomNumber)

Delete a room

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.RoomApi();
let roomNumber = 56; // Number | 
apiInstance.roomRoomNumberDelete(roomNumber).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **roomNumber** | **Number**|  | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


## roomRoomNumberGet

> Room roomRoomNumberGet(roomNumber)

Retrieve a room

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.RoomApi();
let roomNumber = 56; // Number | 
apiInstance.roomRoomNumberGet(roomNumber).then((data) => {
  console.log('API called successfully. Returned data: ' + data);
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **roomNumber** | **Number**|  | 

### Return type

[**Room**](Room.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## roomRoomNumberPut

> roomRoomNumberPut(roomNumber, room)

Update/create a room

### Example

```javascript
import Adherent from 'adherent';

let apiInstance = new Adherent.RoomApi();
let roomNumber = 56; // Number | 
let room = new Adherent.Room(); // Room | Room to update
apiInstance.roomRoomNumberPut(roomNumber, room).then(() => {
  console.log('API called successfully.');
}, (error) => {
  console.error(error);
});

```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **roomNumber** | **Number**|  | 
 **room** | [**Room**](Room.md)| Room to update | 

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: Not defined

