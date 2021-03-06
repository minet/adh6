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

export interface MemberStatus { 
    __typename?: string;
    /**
     * The status id :  * `LOGIN_INCORRECT_WRONG_USER` - Some MAC address tried logging in with the wrong username  * `LOGIN_INCORRECT_WRONG_MAC` - The user tried logging in with a MAC address not registered or belonging to another user  * `LOGIN_INCORRECT_WRONG_PASSWORD` - The user tried logging in with the correct MAC address/username combo but an incorrect password  * `LOGIN_INCORRECT_SSL_ERROR` - The user has enabled certificate verification OR another SSL error occurred (invalid time sync...)  * `LOGIN_DEVICE_ERROR` - A device could not be authentified, the other statuses might provide more details 
     */
    status?: MemberStatus.StatusEnum;
    /**
     * Additionnal data regarding this status
     */
    comment?: string;
    /**
     * When this status was last reported
     */
    lastTimestamp?: Date;
}
export namespace MemberStatus {
    export type StatusEnum = 'LOGIN_INCORRECT_WRONG_USER' | 'LOGIN_INCORRECT_WRONG_MAC' | 'LOGIN_INCORRECT_WRONG_PASSWORD' | 'LOGIN_INCORRECT_SSL_ERROR' | 'LOGIN_DEVICE_ERROR';
    export const StatusEnum = {
        INCORRECTWRONGUSER: 'LOGIN_INCORRECT_WRONG_USER' as StatusEnum,
        INCORRECTWRONGMAC: 'LOGIN_INCORRECT_WRONG_MAC' as StatusEnum,
        INCORRECTWRONGPASSWORD: 'LOGIN_INCORRECT_WRONG_PASSWORD' as StatusEnum,
        INCORRECTSSLERROR: 'LOGIN_INCORRECT_SSL_ERROR' as StatusEnum,
        DEVICEERROR: 'LOGIN_DEVICE_ERROR' as StatusEnum
    };
}
