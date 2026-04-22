export function assertNonEmptyString(value: string, fieldName: string) {
  if (!value || !value.trim()) {
    throw new Error(`${fieldName}不能为空`);
  }
}

export function assertNumberInRange(
  value: number,
  fieldName: string,
  min: number,
  max: number,
) {
  if (!Number.isFinite(value) || value < min || value > max) {
    throw new Error(`${fieldName}必须在${min}~${max}之间`);
  }
}

export function assertPositiveInt(value: number, fieldName: string) {
  if (!Number.isInteger(value) || value <= 0) {
    throw new Error(`${fieldName}必须是正整数`);
  }
}

export function assertPositiveIntArray(values: number[], fieldName: string) {
  if (!Array.isArray(values) || values.length === 0) {
    throw new Error(`${fieldName}不能为空`);
  }
  const invalidExists = values.some((item) => !Number.isInteger(item) || item <= 0);
  if (invalidExists) {
    throw new Error(`${fieldName}必须全部为正整数`);
  }
}
