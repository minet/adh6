/**
 * ADH6 API
 * This is the specification for **MiNET**'s ADH6 plaform. Its aim is to manage our users, devices and treasury. 
 *
 * OpenAPI spec version: 2.0.0
 * Contact: equipe@minet.net
 *
 * NOTE: This class is auto generated by the swagger code generator program.
 * https://github.com/swagger-api/swagger-codegen.git
 * Do not edit the class manually.
 */
import { Account } from './account';
import { Member } from './member';
import { PaymentMethod } from './paymentMethod';
import { Product } from './product';

export interface AbstractMembership { 
    __typename?: string;
    /**
     * The UUID associated with this membership request
     */
    readonly uuid?: string;
    /**
     * The requested duration (in days) for this membership
     */
    duration?: AbstractMembership.DurationEnum;
    /**
     * A list of products to buy
     */
    products?: Array<Product | number>;
    /**
     * Whether this is the first membership request ever for this member
     */
    firstTime?: boolean;
    /**
     * The payment method to be used for the transaction
     */
    paymentMethod?: PaymentMethod | number;
    /**
     * The source account from which to execute the transaction
     */
    account?: Account | number;
    /**
     * The member to whom this membership applies
     */
    member?: Member | number;
    /**
     * The current status of this membership request:  * `INITIAL` - Just created  * `PENDING_RULES` - Waiting for the member to sign the rules  * `PENDING_PAYMENT_INITIAL` - Initiating the payment flow  * `PENDING_PAYMENT` - During the payment flow  * `PENDING_PAYMENT_VALIDATION` - After the payment flow, waiting for confirmation  * `COMPLETE` - The membership request is completed  * `CANCELLED` - The membership has been cancelled  * `ABORTED` - The membership request flow was aborted Do note that some of the steps may be skipped depending on the payment method, whether or not this is the member's first membership request etc. 
     */
    status?: AbstractMembership.StatusEnum;
    /**
     * The date-time at which this membership request was first created
     */
    createdAt?: Date;
    /**
     * The date-time at which this membership request was last updated
     */
    updatedAt?: Date;
}
export namespace AbstractMembership {
    export type DurationEnum = 30 | 60 | 90 | 120 | 150 | 180 | 360;
    export const DurationEnum = {
        NUMBER_30: 30 as DurationEnum,
        NUMBER_60: 60 as DurationEnum,
        NUMBER_90: 90 as DurationEnum,
        NUMBER_120: 120 as DurationEnum,
        NUMBER_150: 150 as DurationEnum,
        NUMBER_180: 180 as DurationEnum,
        NUMBER_360: 360 as DurationEnum
    };
    export type StatusEnum = 'INITIAL' | 'PENDING_RULES' | 'PENDING_PAYMENT_INITIAL' | 'PENDING_PAYMENT' | 'PENDING_PAYMENT_VALIDATION' | 'COMPLETE' | 'CANCELLED' | 'ABORTED';
    export const StatusEnum = {
        INITIAL: 'INITIAL' as StatusEnum,
        PENDINGRULES: 'PENDING_RULES' as StatusEnum,
        PENDINGPAYMENTINITIAL: 'PENDING_PAYMENT_INITIAL' as StatusEnum,
        PENDINGPAYMENT: 'PENDING_PAYMENT' as StatusEnum,
        PENDINGPAYMENTVALIDATION: 'PENDING_PAYMENT_VALIDATION' as StatusEnum,
        COMPLETE: 'COMPLETE' as StatusEnum,
        CANCELLED: 'CANCELLED' as StatusEnum,
        ABORTED: 'ABORTED' as StatusEnum
    };
}
