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

export interface Body { 
    /**
     * The plaintext password to use
     */
    password?: string;
    /**
     * The md4-hashed password to use. MD4 is obv. long-deprecated but we use NTLM for PEAP authentication...
     */
    hashedPassword?: string;
}