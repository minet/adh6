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
/* tslint:disable:no-unused-variable member-ordering */

import { Inject, Injectable, Optional }                      from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams,
         HttpResponse, HttpEvent }                           from '@angular/common/http';
import { CustomHttpUrlEncodingCodec }                        from '../encoder';

import { Observable }                                        from 'rxjs';

import { Product } from '../model/product';
import { ProductPatchRequest } from '../model/productPatchRequest';

import { BASE_PATH, COLLECTION_FORMATS }                     from '../variables';
import { Configuration }                                     from '../configuration';


@Injectable({
  providedIn: 'root'
})
export class ProductService {

    protected basePath = 'http://localhost/api';
    public defaultHeaders = new HttpHeaders();
    public configuration = new Configuration();

    constructor(protected httpClient: HttpClient, @Optional()@Inject(BASE_PATH) basePath: string, @Optional() configuration: Configuration) {

        if (configuration) {
            this.configuration = configuration;
            this.configuration.basePath = configuration.basePath || basePath || this.basePath;

        } else {
            this.configuration.basePath = basePath || this.basePath;
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
     * Filter products
     * 
     * @param limit Limit the number of products returned in the result. Default is 100
     * @param offset Skip the first n results
     * @param terms The generic search terms (will search in any field)
     * @param name Filter by name
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public productGet(limit?: number, offset?: number, terms?: string, name?: string, observe?: 'body', reportProgress?: boolean): Observable<Array<Product>>;
    public productGet(limit?: number, offset?: number, terms?: string, name?: string, observe?: 'response', reportProgress?: boolean): Observable<HttpResponse<Array<Product>>>;
    public productGet(limit?: number, offset?: number, terms?: string, name?: string, observe?: 'events', reportProgress?: boolean): Observable<HttpEvent<Array<Product>>>;
    public productGet(limit?: number, offset?: number, terms?: string, name?: string, observe: any = 'body', reportProgress: boolean = false ): Observable<any> {

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
        if (name !== undefined && name !== null) {
            queryParameters = queryParameters.set('name', <any>name);
        }

        let headers = this.defaultHeaders;

        // to determine the Accept header
        const httpHeaderAccepts: string[] = [
            'application/json'
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected !== undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
        ];

        return this.httpClient.get<Array<Product>>(`${this.configuration.basePath}/product/`,
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
     * Create product
     * 
     * @param product New values of the product
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public productPost(product: Product, observe?: 'body', reportProgress?: boolean): Observable<any>;
    public productPost(product: Product, observe?: 'response', reportProgress?: boolean): Observable<HttpResponse<any>>;
    public productPost(product: Product, observe?: 'events', reportProgress?: boolean): Observable<HttpEvent<any>>;
    public productPost(product: Product, observe: any = 'body', reportProgress: boolean = false ): Observable<any> {
        if (product === null || product === undefined) {
            throw new Error('Required parameter product was null or undefined when calling productPost.');
        }

        let headers = this.defaultHeaders;

        // to determine the Accept header
        const httpHeaderAccepts: string[] = [
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected !== undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
            'application/json'
        ];
        const httpContentTypeSelected: string | undefined = this.configuration.selectHeaderContentType(consumes);
        if (httpContentTypeSelected !== undefined) {
            headers = headers.set('Content-Type', httpContentTypeSelected);
        }

        return this.httpClient.post<any>(`${this.configuration.basePath}/product/`,
            product,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Retrieve
     * 
     * @param productId The id of the product that needs to be fetched.
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public productProductIdGet(productId: string, observe?: 'body', reportProgress?: boolean): Observable<Product>;
    public productProductIdGet(productId: string, observe?: 'response', reportProgress?: boolean): Observable<HttpResponse<Product>>;
    public productProductIdGet(productId: string, observe?: 'events', reportProgress?: boolean): Observable<HttpEvent<Product>>;
    public productProductIdGet(productId: string, observe: any = 'body', reportProgress: boolean = false ): Observable<any> {
        if (productId === null || productId === undefined) {
            throw new Error('Required parameter productId was null or undefined when calling productProductIdGet.');
        }

        let headers = this.defaultHeaders;

        // to determine the Accept header
        const httpHeaderAccepts: string[] = [
            'application/json'
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected !== undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
        ];

        return this.httpClient.get<Product>(`${this.configuration.basePath}/product/${encodeURIComponent(String(productId))}`,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Partially update
     * 
     * @param productId id of the product will be updated
     * @param productPatchRequest New values of the product
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public productProductIdPatch(productId: number, productPatchRequest: ProductPatchRequest, observe?: 'body', reportProgress?: boolean): Observable<any>;
    public productProductIdPatch(productId: number, productPatchRequest: ProductPatchRequest, observe?: 'response', reportProgress?: boolean): Observable<HttpResponse<any>>;
    public productProductIdPatch(productId: number, productPatchRequest: ProductPatchRequest, observe?: 'events', reportProgress?: boolean): Observable<HttpEvent<any>>;
    public productProductIdPatch(productId: number, productPatchRequest: ProductPatchRequest, observe: any = 'body', reportProgress: boolean = false ): Observable<any> {
        if (productId === null || productId === undefined) {
            throw new Error('Required parameter productId was null or undefined when calling productProductIdPatch.');
        }
        if (productPatchRequest === null || productPatchRequest === undefined) {
            throw new Error('Required parameter productPatchRequest was null or undefined when calling productProductIdPatch.');
        }

        let headers = this.defaultHeaders;

        // to determine the Accept header
        const httpHeaderAccepts: string[] = [
        ];
        const httpHeaderAcceptSelected: string | undefined = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        if (httpHeaderAcceptSelected !== undefined) {
            headers = headers.set('Accept', httpHeaderAcceptSelected);
        }

        // to determine the Content-Type header
        const consumes: string[] = [
            'application/json'
        ];
        const httpContentTypeSelected: string | undefined = this.configuration.selectHeaderContentType(consumes);
        if (httpContentTypeSelected !== undefined) {
            headers = headers.set('Content-Type', httpContentTypeSelected);
        }

        return this.httpClient.patch<any>(`${this.configuration.basePath}/product/${encodeURIComponent(String(productId))}`,
            productPatchRequest,
            {
                withCredentials: this.configuration.withCredentials,
                headers: headers,
                observe: observe,
                reportProgress: reportProgress
            }
        );
    }

}
