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
import { ModelSwitch } from './modelSwitch';
import { Room } from './room';

export interface AbstractPort { 
    /**
     * The unique identifier of this port
     */
    readonly id?: number;
    /**
     * The friendly (Cisco) number of this port
     */
    portNumber?: string;
    /**
     * The oid of this port for SNMP access
     */
    oid?: string;
    /**
     * The room this port is in
     */
    room?: Room | number;
    /**
     * The switch this port is a member of
     */
    _switch?: ModelSwitch | number;
}