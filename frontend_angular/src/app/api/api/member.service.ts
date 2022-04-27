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
 *//* eslint-disable @typescript-eslint/no-unused-vars, @typescript-eslint/member-ordering */

import { Inject, Injectable, Optional }                      from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams,
         HttpResponse, HttpEvent }                           from '@angular/common/http';
import { CustomHttpUrlEncodingCodec }                        from '../encoder';

import { Observable }                                        from 'rxjs';

import { AbstractMember } from '../model/abstractMember';
import { Body } from '../model/body';
import { Member } from '../model/member';
import { MemberStatus } from '../model/memberStatus';

import { BASE_PATH, COLLECTION_FORMATS }                     from '../variables';
import { Configuration }                                     from '../configuration';


@Injectable()
export class MemberService {

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
     * Retrieves if the hosting charter has been signed
     * 
     * @param id The id of the account that needs to be fetched.
     * @param charterId The unique identifier of the charter: 1 for MiNET and 2 for Hosting
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public charterGet(id: number, charterId: number, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<Date>;
    public charterGet(id: number, charterId: number, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<Date>>;
    public charterGet(id: number, charterId: number, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<Date>>;
    public charterGet(id: number, charterId: number, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling charterGet.');
        }

        if (charterId === null || charterId === undefined) {
            throw new Error('Required parameter charterId was null or undefined when calling charterGet.');
        }

        let headers = this.defaultHeaders;

        // authentication (ApiKeyAuth) required
        if (this.configuration.apiKeys["X-API-KEY"]) {
            headers = headers.set('X-API-KEY', this.configuration.apiKeys["X-API-KEY"]);
        }

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
        return this.httpClient.request<Date>('get',`${this.basePath}/member/${encodeURIComponent(String(id))}/charter/${encodeURIComponent(String(charterId))}`,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Update if the hosting/MiNET charter has been signed
     * 
     * @param id The id of the account that needs to be fetched.
     * @param charterId The unique identifier of the charter: 1 for MiNET and 2 for Hosting
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public charterPut(id: number, charterId: number, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<any>;
    public charterPut(id: number, charterId: number, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<any>>;
    public charterPut(id: number, charterId: number, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<any>>;
    public charterPut(id: number, charterId: number, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling charterPut.');
        }

        if (charterId === null || charterId === undefined) {
            throw new Error('Required parameter charterId was null or undefined when calling charterPut.');
        }

        let headers = this.defaultHeaders;

        // authentication (ApiKeyAuth) required
        if (this.configuration.apiKeys["X-API-KEY"]) {
            headers = headers.set('X-API-KEY', this.configuration.apiKeys["X-API-KEY"]);
        }

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
        return this.httpClient.request<any>('put',`${this.basePath}/member/${encodeURIComponent(String(id))}/charter/${encodeURIComponent(String(charterId))}`,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Filter members
     * 
     * @param limit Limit the number of results returned
     * @param offset Skip the first n results
     * @param terms The generic search terms (will search in any field)
     * @param filter Filters by various properties
     * @param only Limit to specific attributes
     * @param since Filter member that have departureDate after
     * @param until Filter member that have departureDate before
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public memberGet(limit?: number, offset?: number, terms?: string, filter?: any, only?: Array<string>, since?: Date, until?: Date, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<Array<AbstractMember>>;
    public memberGet(limit?: number, offset?: number, terms?: string, filter?: any, only?: Array<string>, since?: Date, until?: Date, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<Array<AbstractMember>>>;
    public memberGet(limit?: number, offset?: number, terms?: string, filter?: any, only?: Array<string>, since?: Date, until?: Date, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<Array<AbstractMember>>>;
    public memberGet(limit?: number, offset?: number, terms?: string, filter?: any, only?: Array<string>, since?: Date, until?: Date, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {








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
        if (only) {  
            queryParameters = queryParameters.set('only', only.join(COLLECTION_FORMATS['csv']));
        }
        if (since !== undefined && since !== null) {
            queryParameters = queryParameters.set('since', <any>since.toISOString());
        }
        if (until !== undefined && until !== null) {
            queryParameters = queryParameters.set('until', <any>until.toISOString());
        }

        let headers = this.defaultHeaders;

        // authentication (ApiKeyAuth) required
        if (this.configuration.apiKeys["X-API-KEY"]) {
            headers = headers.set('X-API-KEY', this.configuration.apiKeys["X-API-KEY"]);
        }

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
        return this.httpClient.request<Array<AbstractMember>>('get',`${this.basePath}/member/`,
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
     * Delete a member
     * 
     * @param id The id of the account that needs to be fetched.
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public memberIdDelete(id: number, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<any>;
    public memberIdDelete(id: number, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<any>>;
    public memberIdDelete(id: number, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<any>>;
    public memberIdDelete(id: number, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling memberIdDelete.');
        }

        let headers = this.defaultHeaders;

        // authentication (ApiKeyAuth) required
        if (this.configuration.apiKeys["X-API-KEY"]) {
            headers = headers.set('X-API-KEY', this.configuration.apiKeys["X-API-KEY"]);
        }

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
        return this.httpClient.request<any>('delete',`${this.basePath}/member/${encodeURIComponent(String(id))}`,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Retrieve a member
     * 
     * @param id The id of the account that needs to be fetched.
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public memberIdGet(id: number, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<Member>;
    public memberIdGet(id: number, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<Member>>;
    public memberIdGet(id: number, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<Member>>;
    public memberIdGet(id: number, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling memberIdGet.');
        }

        let headers = this.defaultHeaders;

        // authentication (ApiKeyAuth) required
        if (this.configuration.apiKeys["X-API-KEY"]) {
            headers = headers.set('X-API-KEY', this.configuration.apiKeys["X-API-KEY"]);
        }

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
        return this.httpClient.request<Member>('get',`${this.basePath}/member/${encodeURIComponent(String(id))}`,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Retrieve the most recent logs of a member
     * 
     * @param id The id of the account that needs to be fetched.
     * @param dhcp Whether to fetch DHCP logs
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public memberIdLogsGet(id: number, dhcp?: boolean, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<Array<string>>;
    public memberIdLogsGet(id: number, dhcp?: boolean, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<Array<string>>>;
    public memberIdLogsGet(id: number, dhcp?: boolean, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<Array<string>>>;
    public memberIdLogsGet(id: number, dhcp?: boolean, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling memberIdLogsGet.');
        }


        let queryParameters = new HttpParams({encoder: new CustomHttpUrlEncodingCodec()});
        if (dhcp !== undefined && dhcp !== null) {
            queryParameters = queryParameters.set('dhcp', <any>dhcp);
        }

        let headers = this.defaultHeaders;

        // authentication (ApiKeyAuth) required
        if (this.configuration.apiKeys["X-API-KEY"]) {
            headers = headers.set('X-API-KEY', this.configuration.apiKeys["X-API-KEY"]);
        }

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
        return this.httpClient.request<Array<string>>('get',`${this.basePath}/member/${encodeURIComponent(String(id))}/logs/`,
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
     * Update the password of a member
     * 
     * @param body The new value for the password, either in plaintext or pre-hashed client-side
     * @param id The id of the account that needs to be fetched.
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public memberIdPasswordPut(body: Body, id: number, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<any>;
    public memberIdPasswordPut(body: Body, id: number, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<any>>;
    public memberIdPasswordPut(body: Body, id: number, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<any>>;
    public memberIdPasswordPut(body: Body, id: number, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (body === null || body === undefined) {
            throw new Error('Required parameter body was null or undefined when calling memberIdPasswordPut.');
        }

        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling memberIdPasswordPut.');
        }

        let headers = this.defaultHeaders;

        // authentication (ApiKeyAuth) required
        if (this.configuration.apiKeys["X-API-KEY"]) {
            headers = headers.set('X-API-KEY', this.configuration.apiKeys["X-API-KEY"]);
        }

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
        return this.httpClient.request<any>('put',`${this.basePath}/member/${encodeURIComponent(String(id))}/password/`,
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
     * Partially update a member
     * 
     * @param body The new values for this member
     * @param id The id of the account that needs to be fetched.
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public memberIdPatch(body: AbstractMember, id: number, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<any>;
    public memberIdPatch(body: AbstractMember, id: number, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<any>>;
    public memberIdPatch(body: AbstractMember, id: number, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<any>>;
    public memberIdPatch(body: AbstractMember, id: number, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (body === null || body === undefined) {
            throw new Error('Required parameter body was null or undefined when calling memberIdPatch.');
        }

        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling memberIdPatch.');
        }

        let headers = this.defaultHeaders;

        // authentication (ApiKeyAuth) required
        if (this.configuration.apiKeys["X-API-KEY"]) {
            headers = headers.set('X-API-KEY', this.configuration.apiKeys["X-API-KEY"]);
        }

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
        return this.httpClient.request<any>('patch',`${this.basePath}/member/${encodeURIComponent(String(id))}`,
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
     * Update a member
     * 
     * @param body The new values for this member
     * @param id The id of the account that needs to be fetched.
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public memberIdPut(body: Member, id: number, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<any>;
    public memberIdPut(body: Member, id: number, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<any>>;
    public memberIdPut(body: Member, id: number, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<any>>;
    public memberIdPut(body: Member, id: number, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (body === null || body === undefined) {
            throw new Error('Required parameter body was null or undefined when calling memberIdPut.');
        }

        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling memberIdPut.');
        }

        let headers = this.defaultHeaders;

        // authentication (ApiKeyAuth) required
        if (this.configuration.apiKeys["X-API-KEY"]) {
            headers = headers.set('X-API-KEY', this.configuration.apiKeys["X-API-KEY"]);
        }

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
        return this.httpClient.request<any>('put',`${this.basePath}/member/${encodeURIComponent(String(id))}`,
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
     * Retrieves some common status updates concerning a member
     * 
     * @param id The id of the account that needs to be fetched.
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public memberIdStatusesGet(id: number, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<Array<MemberStatus>>;
    public memberIdStatusesGet(id: number, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<Array<MemberStatus>>>;
    public memberIdStatusesGet(id: number, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<Array<MemberStatus>>>;
    public memberIdStatusesGet(id: number, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling memberIdStatusesGet.');
        }

        let headers = this.defaultHeaders;

        // authentication (ApiKeyAuth) required
        if (this.configuration.apiKeys["X-API-KEY"]) {
            headers = headers.set('X-API-KEY', this.configuration.apiKeys["X-API-KEY"]);
        }

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
        return this.httpClient.request<Array<MemberStatus>>('get',`${this.basePath}/member/${encodeURIComponent(String(id))}/statuses/`,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Create a member
     * 
     * @param body The member to create
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     * @param criticalError flag to set whether an error on this request should me considered critical for the application flow
     */
    public memberPost(body: Member, observe?: 'body', reportProgress?: boolean, criticalError?: boolean): Observable<Member>;
    public memberPost(body: Member, observe?: 'response', reportProgress?: boolean, criticalError?: boolean): Observable<HttpResponse<Member>>;
    public memberPost(body: Member, observe?: 'events', reportProgress?: boolean, criticalError?: boolean): Observable<HttpEvent<Member>>;
    public memberPost(body: Member, observe: any = 'body', reportProgress: boolean = false, criticalError: boolean = true ): Observable<any> {

        if (body === null || body === undefined) {
            throw new Error('Required parameter body was null or undefined when calling memberPost.');
        }

        let headers = this.defaultHeaders;

        // authentication (ApiKeyAuth) required
        if (this.configuration.apiKeys["X-API-KEY"]) {
            headers = headers.set('X-API-KEY', this.configuration.apiKeys["X-API-KEY"]);
        }

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
        return this.httpClient.request<Member>('post',`${this.basePath}/member/`,
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
