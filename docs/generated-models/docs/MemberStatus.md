# MemberStatus

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | The status id :  * &#x60;LOGIN_INCORRECT_WRONG_USER&#x60; - Some MAC address tried logging in with the wrong username  * &#x60;LOGIN_INCORRECT_WRONG_MAC&#x60; - The user tried logging in with a MAC address not registered or belonging to another user  * &#x60;LOGIN_INCORRECT_WRONG_PASSWORD&#x60; - The user tried logging in with the correct MAC address/username combo but an incorrect password  * &#x60;LOGIN_INCORRECT_SSL_ERROR&#x60; - The user has enabled certificate verification OR another SSL error occurred (invalid time sync...)  * &#x60;LOGIN_DEVICE_ERROR&#x60; - A device could not be authentified, the other statuses might provide more details  | [optional] 
**comment** | **str** | Additionnal data regarding this status | [optional] 
**last_timestamp** | **datetime** | When this status was last reported | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

