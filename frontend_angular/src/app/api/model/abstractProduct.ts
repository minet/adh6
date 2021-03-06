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

export interface AbstractProduct { 
    __typename?: string;
    /**
     * The unique identifier of this product
     */
    readonly id?: number;
    /**
     * The buying price of this product
     */
    buyingPrice?: number;
    /**
     * The selling price of this product
     */
    sellingPrice?: number;
    /**
     * The friendly name of this product
     */
    name?: string;
}
