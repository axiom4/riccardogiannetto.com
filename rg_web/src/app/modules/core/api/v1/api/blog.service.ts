/**
 * Riccardo Giannetto Gallery API
 *
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
/* tslint:disable:no-unused-variable member-ordering */

import { Inject, Injectable, Optional }                      from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams,
         HttpResponse, HttpEvent, HttpParameterCodec, HttpContext 
        }       from '@angular/common/http';
import { CustomHttpParameterCodec }                          from '../encoder';
import { Observable }                                        from 'rxjs';

// @ts-ignore
import { Category } from '../model/category';
// @ts-ignore
import { ListCategories200Response } from '../model/listCategories200Response';
// @ts-ignore
import { ListPages200Response } from '../model/listPages200Response';
// @ts-ignore
import { ListPosts200Response } from '../model/listPosts200Response';
// @ts-ignore
import { Page } from '../model/page';
// @ts-ignore
import { Post } from '../model/post';

// @ts-ignore
import { BASE_PATH, COLLECTION_FORMATS }                     from '../variables';
import { Configuration }                                     from '../configuration';
import { BaseService } from '../api.base.service';
import {
    BlogServiceInterface,
    ListCategoriesRequestParams,
    ListPagesRequestParams,
    ListPostsRequestParams,
    RetrieveCategoryRequestParams,
    RetrievePageRequestParams,
    RetrievePostRequestParams
} from './blog.serviceInterface';



@Injectable({
  providedIn: 'root'
})
export class BlogService extends BaseService implements BlogServiceInterface {

    constructor(protected httpClient: HttpClient, @Optional() @Inject(BASE_PATH) basePath: string|string[], @Optional() configuration?: Configuration) {
        super(basePath, configuration);
    }

    /**
     * API endpoint that allows groups to be viewed or edited.
     * @param requestParameters
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public listCategories(requestParameters?: ListCategoriesRequestParams, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<ListCategories200Response>;
    public listCategories(requestParameters?: ListCategoriesRequestParams, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<ListCategories200Response>>;
    public listCategories(requestParameters?: ListCategoriesRequestParams, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<ListCategories200Response>>;
    public listCategories(requestParameters?: ListCategoriesRequestParams, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        const limit = requestParameters?.limit;
        const offset = requestParameters?.offset;

        let localVarQueryParameters = new HttpParams({encoder: this.encoder});
        localVarQueryParameters = this.addToHttpParams(localVarQueryParameters,
          <any>limit, 'limit');
        localVarQueryParameters = this.addToHttpParams(localVarQueryParameters,
          <any>offset, 'offset');

        let localVarHeaders = this.defaultHeaders;

        const localVarHttpHeaderAcceptSelected: string | undefined = options?.httpHeaderAccept ?? this.configuration.selectHeaderAccept([
            'application/json'
        ]);
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        const localVarHttpContext: HttpContext = options?.context ?? new HttpContext();

        const localVarTransferCache: boolean = options?.transferCache ?? true;


        let responseType_: 'text' | 'json' | 'blob' = 'json';
        if (localVarHttpHeaderAcceptSelected) {
            if (localVarHttpHeaderAcceptSelected.startsWith('text')) {
                responseType_ = 'text';
            } else if (this.configuration.isJsonMime(localVarHttpHeaderAcceptSelected)) {
                responseType_ = 'json';
            } else {
                responseType_ = 'blob';
            }
        }

        let localVarPath = `/blog/categories`;
        return this.httpClient.request<ListCategories200Response>('get', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                params: localVarQueryParameters,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * 
     * @param requestParameters
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public listPages(requestParameters?: ListPagesRequestParams, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<ListPages200Response>;
    public listPages(requestParameters?: ListPagesRequestParams, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<ListPages200Response>>;
    public listPages(requestParameters?: ListPagesRequestParams, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<ListPages200Response>>;
    public listPages(requestParameters?: ListPagesRequestParams, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        const limit = requestParameters?.limit;
        const offset = requestParameters?.offset;

        let localVarQueryParameters = new HttpParams({encoder: this.encoder});
        localVarQueryParameters = this.addToHttpParams(localVarQueryParameters,
          <any>limit, 'limit');
        localVarQueryParameters = this.addToHttpParams(localVarQueryParameters,
          <any>offset, 'offset');

        let localVarHeaders = this.defaultHeaders;

        const localVarHttpHeaderAcceptSelected: string | undefined = options?.httpHeaderAccept ?? this.configuration.selectHeaderAccept([
            'application/json'
        ]);
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        const localVarHttpContext: HttpContext = options?.context ?? new HttpContext();

        const localVarTransferCache: boolean = options?.transferCache ?? true;


        let responseType_: 'text' | 'json' | 'blob' = 'json';
        if (localVarHttpHeaderAcceptSelected) {
            if (localVarHttpHeaderAcceptSelected.startsWith('text')) {
                responseType_ = 'text';
            } else if (this.configuration.isJsonMime(localVarHttpHeaderAcceptSelected)) {
                responseType_ = 'json';
            } else {
                responseType_ = 'blob';
            }
        }

        let localVarPath = `/blog/pages`;
        return this.httpClient.request<ListPages200Response>('get', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                params: localVarQueryParameters,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * 
     * @param requestParameters
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public listPosts(requestParameters?: ListPostsRequestParams, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<ListPosts200Response>;
    public listPosts(requestParameters?: ListPostsRequestParams, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<ListPosts200Response>>;
    public listPosts(requestParameters?: ListPostsRequestParams, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<ListPosts200Response>>;
    public listPosts(requestParameters?: ListPostsRequestParams, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        const page = requestParameters?.page;
        const pageSize = requestParameters?.pageSize;
        const categoriesName = requestParameters?.categoriesName;
        const search = requestParameters?.search;
        const ordering = requestParameters?.ordering;

        let localVarQueryParameters = new HttpParams({encoder: this.encoder});
        localVarQueryParameters = this.addToHttpParams(localVarQueryParameters,
          <any>page, 'page');
        localVarQueryParameters = this.addToHttpParams(localVarQueryParameters,
          <any>pageSize, 'page_size');
        localVarQueryParameters = this.addToHttpParams(localVarQueryParameters,
          <any>categoriesName, 'categories__name');
        localVarQueryParameters = this.addToHttpParams(localVarQueryParameters,
          <any>search, 'search');
        localVarQueryParameters = this.addToHttpParams(localVarQueryParameters,
          <any>ordering, 'ordering');

        let localVarHeaders = this.defaultHeaders;

        const localVarHttpHeaderAcceptSelected: string | undefined = options?.httpHeaderAccept ?? this.configuration.selectHeaderAccept([
            'application/json'
        ]);
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        const localVarHttpContext: HttpContext = options?.context ?? new HttpContext();

        const localVarTransferCache: boolean = options?.transferCache ?? true;


        let responseType_: 'text' | 'json' | 'blob' = 'json';
        if (localVarHttpHeaderAcceptSelected) {
            if (localVarHttpHeaderAcceptSelected.startsWith('text')) {
                responseType_ = 'text';
            } else if (this.configuration.isJsonMime(localVarHttpHeaderAcceptSelected)) {
                responseType_ = 'json';
            } else {
                responseType_ = 'blob';
            }
        }

        let localVarPath = `/blog/posts`;
        return this.httpClient.request<ListPosts200Response>('get', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                params: localVarQueryParameters,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * API endpoint that allows groups to be viewed or edited.
     * @param requestParameters
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public retrieveCategory(requestParameters: RetrieveCategoryRequestParams, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<Category>;
    public retrieveCategory(requestParameters: RetrieveCategoryRequestParams, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<Category>>;
    public retrieveCategory(requestParameters: RetrieveCategoryRequestParams, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<Category>>;
    public retrieveCategory(requestParameters: RetrieveCategoryRequestParams, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        const id = requestParameters?.id;
        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling retrieveCategory.');
        }

        let localVarHeaders = this.defaultHeaders;

        const localVarHttpHeaderAcceptSelected: string | undefined = options?.httpHeaderAccept ?? this.configuration.selectHeaderAccept([
            'application/json'
        ]);
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        const localVarHttpContext: HttpContext = options?.context ?? new HttpContext();

        const localVarTransferCache: boolean = options?.transferCache ?? true;


        let responseType_: 'text' | 'json' | 'blob' = 'json';
        if (localVarHttpHeaderAcceptSelected) {
            if (localVarHttpHeaderAcceptSelected.startsWith('text')) {
                responseType_ = 'text';
            } else if (this.configuration.isJsonMime(localVarHttpHeaderAcceptSelected)) {
                responseType_ = 'json';
            } else {
                responseType_ = 'blob';
            }
        }

        let localVarPath = `/blog/categories/${this.configuration.encodeParam({name: "id", value: id, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}`;
        return this.httpClient.request<Category>('get', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * 
     * @param requestParameters
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public retrievePage(requestParameters: RetrievePageRequestParams, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<Page>;
    public retrievePage(requestParameters: RetrievePageRequestParams, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<Page>>;
    public retrievePage(requestParameters: RetrievePageRequestParams, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<Page>>;
    public retrievePage(requestParameters: RetrievePageRequestParams, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        const tag = requestParameters?.tag;
        if (tag === null || tag === undefined) {
            throw new Error('Required parameter tag was null or undefined when calling retrievePage.');
        }

        let localVarHeaders = this.defaultHeaders;

        const localVarHttpHeaderAcceptSelected: string | undefined = options?.httpHeaderAccept ?? this.configuration.selectHeaderAccept([
            'application/json'
        ]);
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        const localVarHttpContext: HttpContext = options?.context ?? new HttpContext();

        const localVarTransferCache: boolean = options?.transferCache ?? true;


        let responseType_: 'text' | 'json' | 'blob' = 'json';
        if (localVarHttpHeaderAcceptSelected) {
            if (localVarHttpHeaderAcceptSelected.startsWith('text')) {
                responseType_ = 'text';
            } else if (this.configuration.isJsonMime(localVarHttpHeaderAcceptSelected)) {
                responseType_ = 'json';
            } else {
                responseType_ = 'blob';
            }
        }

        let localVarPath = `/blog/pages/${this.configuration.encodeParam({name: "tag", value: tag, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}`;
        return this.httpClient.request<Page>('get', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * 
     * @param requestParameters
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public retrievePost(requestParameters: RetrievePostRequestParams, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<Post>;
    public retrievePost(requestParameters: RetrievePostRequestParams, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<Post>>;
    public retrievePost(requestParameters: RetrievePostRequestParams, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<Post>>;
    public retrievePost(requestParameters: RetrievePostRequestParams, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        const id = requestParameters?.id;
        if (id === null || id === undefined) {
            throw new Error('Required parameter id was null or undefined when calling retrievePost.');
        }
        const categoriesName = requestParameters?.categoriesName;
        const search = requestParameters?.search;
        const ordering = requestParameters?.ordering;

        let localVarQueryParameters = new HttpParams({encoder: this.encoder});
        localVarQueryParameters = this.addToHttpParams(localVarQueryParameters,
          <any>categoriesName, 'categories__name');
        localVarQueryParameters = this.addToHttpParams(localVarQueryParameters,
          <any>search, 'search');
        localVarQueryParameters = this.addToHttpParams(localVarQueryParameters,
          <any>ordering, 'ordering');

        let localVarHeaders = this.defaultHeaders;

        const localVarHttpHeaderAcceptSelected: string | undefined = options?.httpHeaderAccept ?? this.configuration.selectHeaderAccept([
            'application/json'
        ]);
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        const localVarHttpContext: HttpContext = options?.context ?? new HttpContext();

        const localVarTransferCache: boolean = options?.transferCache ?? true;


        let responseType_: 'text' | 'json' | 'blob' = 'json';
        if (localVarHttpHeaderAcceptSelected) {
            if (localVarHttpHeaderAcceptSelected.startsWith('text')) {
                responseType_ = 'text';
            } else if (this.configuration.isJsonMime(localVarHttpHeaderAcceptSelected)) {
                responseType_ = 'json';
            } else {
                responseType_ = 'blob';
            }
        }

        let localVarPath = `/blog/posts/${this.configuration.encodeParam({name: "id", value: id, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}`;
        return this.httpClient.request<Post>('get', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                params: localVarQueryParameters,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

}
