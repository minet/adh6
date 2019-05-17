/**
 * Adherent
 * Adherent api
 *
 * The version of the OpenAPI document: 1.0.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


export interface Account { 
    /**
     * Account state
     */
    actif: boolean;
    /**
     * ID of the account
     */
    id?: number;
    /**
     * Name of the account
     */
    name?: string;
    /**
     * ID of the type of account
     */
    type: number;
}
