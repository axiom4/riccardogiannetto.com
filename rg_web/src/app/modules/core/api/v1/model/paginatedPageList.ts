/**
 * Riccardo Giannetto  API
 *
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
import { Page } from './page';


export interface PaginatedPageList { 
    count: number;
    next?: string;
    previous?: string;
    results: Array<Page>;
}

