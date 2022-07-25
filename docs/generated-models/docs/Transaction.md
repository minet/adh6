# Transaction

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The unique identifier of this transaction | [optional] 
**name** | **str** | The description of this transaction | 
**src** | **int** | The source account of this transaction | 
**dst** | **int** | The destination account of this transaction | 
**timestamp** | **datetime** | The date-time at which this transaction was executed | [optional] 
**payment_method** | **int** | The payment method used for this transaction | 
**value** | **float** | The unsigned value of this transaction | 
**attachments** | **list[str]** | The list of attachments linked with this transaction | [optional] 
**author** | **int** | The member who executed this transaction | [optional] 
**pending_validation** | **bool** | Whether this transaction is awaiting confirmation from a member with higher privileges | [optional] 
**cashbox** | **str** | Whether to use the cashbox or not | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

