// 백엔드 공통 응답 틀 (backend/app/schemas/common.py 와 같은 형태)
// 성공·실패 판별은 HTTP 상태 코드로 한다. statusCode 는 같은 값을 본문에 한 번 더 적은 것.

export type ApiResponse<T> = {
  statusCode: number;
  code: string;
  data: T;
};

export type FieldError = {
  /** 오류 위치. 예: query.page */
  field: string;
  message: string;
};

export type ApiErrorBody = {
  statusCode: number;
  /** 분기용 값. 예: NOT_FOUND, VALIDATION_ERROR */
  code: string;
  /** 사람에게 보여주는 문구 */
  message: string;
  errors: FieldError[];
};
