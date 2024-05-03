export * from './blog.service';
import { BlogService } from './blog.service';
export * from './blog.serviceInterface';
export * from './portfolio.service';
import { PortfolioService } from './portfolio.service';
export * from './portfolio.serviceInterface';
export const APIS = [BlogService, PortfolioService];
