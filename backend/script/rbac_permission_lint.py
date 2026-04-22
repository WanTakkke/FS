import re
import sys
from collections import Counter
from pathlib import Path


PERMISSION_PATTERN = re.compile(r"^[a-z][a-z0-9_]*:[a-z][a-z0-9_]*(?::[a-z][a-z0-9_]*)?$")
REQUIRE_PERMISSION_PATTERN = re.compile(r'require_permission\("([^"]+)"\)')
SQL_PERMISSION_PATTERN_1 = re.compile(r"SELECT\s+'[^']+'\s+AS\s+name,\s+'([^']+)'\s+AS\s+code")
SQL_PERMISSION_PATTERN_2 = re.compile(r"UNION ALL SELECT\s+'[^']+',\s*'([^']+)'")


def collect_codes_from_python(backend_dir: Path) -> list[str]:
    codes: list[str] = []
    py_files = list((backend_dir / "controller").glob("*.py"))
    py_files.append(backend_dir / "agent" / "ai.py")
    for file_path in py_files:
        if not file_path.exists():
            continue
        text = file_path.read_text(encoding="utf-8")
        codes.extend(REQUIRE_PERMISSION_PATTERN.findall(text))
    return codes


def collect_codes_from_sql(sql_file: Path) -> list[str]:
    text = sql_file.read_text(encoding="utf-8")
    start = text.find("FROM (")
    end = text.find(") p", start + 1)
    target = text[start:end] if start >= 0 and end > start else text
    codes = SQL_PERMISSION_PATTERN_1.findall(target)
    codes.extend(SQL_PERMISSION_PATTERN_2.findall(target))
    return codes


def main():
    backend_dir = Path(__file__).resolve().parent.parent
    sql_file = backend_dir / "sql" / "rbac_init.sql"
    if not sql_file.exists():
        print(f"FAIL: 找不到文件 {sql_file}", file=sys.stderr)
        sys.exit(1)

    code_codes = collect_codes_from_python(backend_dir)
    sql_codes = collect_codes_from_sql(sql_file)

    code_counter = Counter(code_codes)
    sql_counter = Counter(sql_codes)

    sql_duplicates = sorted([k for k, v in sql_counter.items() if v > 1])

    code_bad_format = sorted([c for c in set(code_codes) if not PERMISSION_PATTERN.match(c)])
    sql_bad_format = sorted([c for c in set(sql_codes) if not PERMISSION_PATTERN.match(c)])

    code_set = set(code_codes)
    sql_set = set(sql_codes)
    missing_in_sql = sorted(code_set - sql_set)
    unused_in_code = sorted(sql_set - code_set)

    print("=== RBAC 权限码治理检查 ===")
    print(f"代码中权限码数量: {len(code_codes)}")
    print(f"SQL中权限码数量: {len(sql_codes)}")
    print(f"代码去重后数量: {len(code_set)}")
    print(f"SQL去重后数量: {len(sql_set)}")

    has_error = False

    if sql_duplicates:
        has_error = True
        print("\n[ERROR] SQL初始化中存在重复权限码:")
        for item in sql_duplicates:
            print(f"- {item} (count={sql_counter[item]})")

    if code_bad_format:
        has_error = True
        print("\n[ERROR] 代码中存在非法权限码格式(应为 module:resource:action):")
        for item in code_bad_format:
            print(f"- {item}")

    if sql_bad_format:
        has_error = True
        print("\n[ERROR] SQL中存在非法权限码格式(应为 module:action 或 module:resource:action):")
        for item in sql_bad_format:
            print(f"- {item}")

    if missing_in_sql:
        has_error = True
        print("\n[ERROR] 代码中使用但SQL未初始化的权限码:")
        for item in missing_in_sql:
            print(f"- {item}")

    if unused_in_code:
        print("\n[WARN] SQL中存在未被代码 require_permission 使用的权限码:")
        for item in unused_in_code:
            print(f"- {item}")

    if has_error:
        print("\nFAIL: 权限码治理检查未通过", file=sys.stderr)
        sys.exit(1)

    print("\nPASS: 权限码治理检查通过")


if __name__ == "__main__":
    main()
