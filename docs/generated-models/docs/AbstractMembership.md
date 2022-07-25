# AbstractMembership

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** | The UUID associated with this membership request | [optional] 
**duration** | **int** | The requested duration (in months) for this membership | [optional] 
**has_room** | **bool** | if the Member ask for a room or not | [optional] 
**products** | **list[int]** | A list of the ids products to buy | [optional] 
**first_time** | **bool** | Whether this is the first membership request ever for this member | [optional] 
**payment_method** | **int** | The payment method id to be used for the transaction | [optional] 
**account** | **int** | The id of the source account from which to execute the transaction | [optional] 
**member** | **int** | The id of the member to whom this membership applies | [optional] 
**status** | **str** | The current status of this membership request:  * &#x60;INITIAL&#x60; - Just created  * &#x60;PENDING_RULES&#x60; - Waiting for the member to sign the rules  * &#x60;PENDING_PAYMENT_INITIAL&#x60; - Initiating the payment flow  * &#x60;PENDING_PAYMENT&#x60; - During the payment flow  * &#x60;PENDING_PAYMENT_VALIDATION&#x60; - After the payment flow, waiting for confirmation  * &#x60;COMPLETE&#x60; - The membership request is completed  * &#x60;CANCELLED&#x60; - The membership has been cancelled  * &#x60;ABORTED&#x60; - The membership request flow was aborted Do note that some of the steps may be skipped depending on the payment method, whether or not this is the member&#x27;s first membership request etc.  | [optional] 
**created_at** | **datetime** | The date-time at which this membership request was first created | [optional] 
**updated_at** | **datetime** | The date-time at which this membership request was last updated | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

