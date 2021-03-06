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
 *//* tslint:disable:no-unused-variable member-ordering */

import { Inject, Injectable, Optional }                      from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams,
         HttpResponse, HttpEvent }                           from '@angular/common/http';
import { CustomHttpUrlEncodingCodec }                        from '../encoder';

import { Observable }                                        from 'rxjs';

import { AbstractSwitch } from '../model/abstractSwitch';
import { ModelSwitch } from '../model/modelSwitch';

import { BASE_PATH, COLLECTION_FORMATS }                     from '../variables';
import { Configuration }                                     from '../configuration';


@Injectable()
export class SwitchService {

    protected basePath = 'https://adh6.minet.net/api/';
    public defaultHeaders = new HttpHeaders();
    public configuration = new Configuration();

    constructor(protected httpClient: HttpClient, @Optional()@Inject(BASE_PATH) basePath: string, @Optional() configuration: Configuration) {
        if (basePath) {
            this.basePath = basePath;
        }
        if (configuration) {
            this.configuration = configuration;
            this.basePath = basePath || configuration.basePath || this.basePath;
        }
    }

    /**
     * @param consumes string[] mime-types
     * @return true: consumes contains 'multipart/form-data', false: otherwise
     */
    private canConsumeForm(consumes: string[]): boolean {
        const form = 'multipart/form-data';
        for (const consume of consumes) {
            if (form === consume) {
                return true;
            }
        }
        return false;
    }


    /**
     * Filter switches
     * 
     * @param limit Limit the number of results returned
     * @param offset Skip the first n results
     * @param terms The generic search terms (will search in any field)
     * @param filter Filters by various properties
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public switchGet(limit?: number, offset?: number, terms?: string, filter?: any, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<Array<ModelSwitch>>;
    public switchGet(limit?: number, offset?: number, terms?: string, filter?: any, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<Array<ModelSwitch>>>;
    public switchGet(limit?: number, offset?: number, terms?: string, filter?: any, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<Array<ModelSwitch>>>;
    public switchGet(limit?: number, offset?: number, terms?: string, filter?: any, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {





        let queryParameters = new HttpParams({encoder: new CustomHttpUrlEncodingCodec()});
        if (limit !== undefined && limit !== null) {
            queryParameters = queryParameters.set('limit', <any>limit);
        }
        if (offset !== undefined && offset !== null) {
            queryParameters = queryParameters.set('offset', <any>offset);
        }
        if (terms !== undefined && terms !== null) {
            queryParameters = queryParameters.set('terms', <any>terms);
        }
        if (filter) {
            for (const key in filter) {
                if (Object.prototype.hasOwnProperty.call(filter, key)) {
                  const value = filter[key];
                  queryParameters = queryParameters.append('filter[' + key + ']', <any>value);
                }
            }
        }

        let headers = this.defaultHeaders;

        // authentication (OAuth2) required
        if (this.configuration.accessToken) {
            const accessToken = typeof this.configuration.accessToken === 'function'
                ? this.configuration.accessToken()
                : this.configuration.accessToken;
            headers = headers.set('Authorization', 'Bearer ' + accessToken);
        }

        // to determine the Accept header
        let httpHeaderAccepts: string[] = [
            'application/json'
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected != undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
        ];

        headers = headers.set('X-Critical-Error', ''+criticalError);
        return this.httpClient.request<Array<ModelSwitch>>('get',`${this.basePath}/switch/`,
            {
                params: queryParameters,
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Create a switch
     * 
     * @param body The switch to create
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public switchPost(body: ModelSwitch, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<ModelSwitch>;
    public switchPost(body: ModelSwitch, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<ModelSwitch>>;
    public switchPost(body: ModelSwitch, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<ModelSwitch>>;
    public switchPost(body: ModelSwitch, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (body === null || body === undefined) {
            throw new Error('Required parameter body was null or undefined when calling switchPost.');
        }

        let headers = this.defaultHeaders;

        // authentication (OAuth2) required
        if (this.configuration.accessToken) {
            const accessToken = typeof this.configuration.accessToken === 'function'
                ? this.configuration.accessToken()
                : this.configuration.accessToken;
            headers = headers.set('Authorization', 'Bearer ' + accessToken);
        }

        // to determine the Accept header
        let httpHeaderAccepts: string[] = [
            'application/json'
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected != undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
            'application/json'
        ];
        const httpContentTypeSelected: string | undefined = this.configuration.selectHeaderContentType(consumes);
        if (httpContentTypeSelected != undefined) {
            headers = headers.set('Content-Type', httpContentTypeSelected);
        }

        headers = headers.set('X-Critical-Error', ''+criticalError);
        return this.httpClient.request<ModelSwitch>('post',`${this.basePath}/switch/`,
            {
                body: body,
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Delete a switch
     * 
     * @param switchId 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public switchSwitchIdDelete(switchId: number, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<any>;
    public switchSwitchIdDelete(switchId: number, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<any>>;
    public switchSwitchIdDelete(switchId: number, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<any>>;
    public switchSwitchIdDelete(switchId: number, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (switchId === null || switchId === undefined) {
            throw new Error('Required parameter switchId was null or undefined when calling switchSwitchIdDelete.');
        }

        let headers = this.defaultHeaders;

        // authentication (OAuth2) required
        if (this.configuration.accessToken) {
            const accessToken = typeof this.configuration.accessToken === 'function'
                ? this.configuration.accessToken()
                : this.configuration.accessToken;
            headers = headers.set('Authorization', 'Bearer ' + accessToken);
        }

        // to determine the Accept header
        let httpHeaderAccepts: string[] = [
            'application/json'
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected != undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
        ];

        headers = headers.set('X-Critical-Error', ''+criticalError);
        return this.httpClient.request<any>('delete',`${this.basePath}/switch/${encodeURIComponent(String(switchId))}`,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Retrieve a switch
     * 
     * @param switchId 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public switchSwitchIdGet(switchId: number, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<ModelSwitch>;
    public switchSwitchIdGet(switchId: number, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<ModelSwitch>>;
    public switchSwitchIdGet(switchId: number, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<ModelSwitch>>;
    public switchSwitchIdGet(switchId: number, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (switchId === null || switchId === undefined) {
            throw new Error('Required parameter switchId was null or undefined when calling switchSwitchIdGet.');
        }

        let headers = this.defaultHeaders;

        // authentication (OAuth2) required
        if (this.configuration.accessToken) {
            const accessToken = typeof this.configuration.accessToken === 'function'
                ? this.configuration.accessToken()
                : this.configuration.accessToken;
            headers = headers.set('Authorization', 'Bearer ' + accessToken);
        }

        // to determine the Accept header
        let httpHeaderAccepts: string[] = [
            'application/json'
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected != undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
        ];

        headers = headers.set('X-Critical-Error', ''+criticalError);
        return this.httpClient.request<ModelSwitch>('get',`${this.basePath}/switch/${encodeURIComponent(String(switchId))}`,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Update a switch
     * 
     * @param body The new values for this switch
     * @param switchId 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public switchSwitchIdPut(body: AbstractSwitch, switchId: number, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<any>;
    public switchSwitchIdPut(body: AbstractSwitch, switchId: number, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<any>>;
    public switchSwitchIdPut(body: AbstractSwitch, switchId: number, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<any>>;
    public switchSwitchIdPut(body: AbstractSwitch, switchId: number, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (body === null || body === undefined) {
            throw new Error('Required parameter body was null or undefined when calling switchSwitchIdPut.');
        }

        if (switchId === null || switchId === undefined) {
            throw new Error('Required parameter switchId was null or undefined when calling switchSwitchIdPut.');
        }

        let headers = this.defaultHeaders;

        // authentication (OAuth2) required
        if (this.configuration.accessToken) {
            const accessToken = typeof this.configuration.accessToken === 'function'
                ? this.configuration.accessToken()
                : this.configuration.accessToken;
            headers = headers.set('Authorization', 'Bearer ' + accessToken);
        }

        // to determine the Accept header
        let httpHeaderAccepts: string[] = [
            'application/json'
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected != undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
            'application/json'
        ];
        const httpContentTypeSelected: string | undefined = this.configuration.selectHeaderContentType(consumes);
        if (httpContentTypeSelected != undefined) {
            headers = headers.set('Content-Type', httpContentTypeSelected);
        }

        headers = headers.set('X-Critical-Error', ''+criticalError);
        return this.httpClient.request<any>('put',`${this.basePath}/switch/${encodeURIComponent(String(switchId))}`,
            {
                body: body,
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

}
