/**
 * Test App API
 *
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
import { User } from './user';


export interface PostPreview { 
    readonly id: number;
    readonly url: string;
    readonly author: User;
    title: string;
    readonly created_at: string;
    image?: string | null;
    categories: Array<string>;
    summary?: string;
}

