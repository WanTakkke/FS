export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface PageParams {
  page: number;
  page_size: number;
}
