/**
 * Riccardo Giannetto Gallery API
 * API app riccardogiannetto.com
 *
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
import { PageAuthor } from './pageAuthor';


export interface Page { 
    readonly id?: number;
    readonly url?: string;
    tag: string;
    author?: PageAuthor;
    title: string;
    body: string;
    readonly created_at?: string;
}

