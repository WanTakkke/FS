import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request


def request_json(method: str, url: str, payload: dict | None = None, token: str | None = None, timeout: int = 10):
    data = None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url=url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
            body = resp.read().decode("utf-8")
            return status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        parsed = {}
        if body:
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = {"raw": body}
        return e.code, parsed


def assert_true(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def check_business_success(status: int, payload: dict, scene: str):
    assert_true(status == 200, f"{scene}: HTTP 状态码异常，期望 200，实际 {status}")
    assert_true(isinstance(payload, dict), f"{scene}: 响应不是 JSON 对象")
    assert_true(payload.get("code") == 200, f"{scene}: 业务码异常，期望 200，实际 {payload.get('code')}, message={payload.get('message')}")


def main():
    parser = argparse.ArgumentParser(description="RBAC 冒烟测试脚本（失败即退出非0）")
    parser.add_argument("--base-url", default="http://localhost:8001", help="后端地址，默认 http://localhost:8001")
    parser.add_argument("--username", required=True, help="登录用户名")
    parser.add_argument("--password", required=True, help="登录密码")
    parser.add_argument("--timeout", type=int, default=12, help="请求超时秒数")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")

    print("[1/6] 登录获取 token ...")
    status, payload = request_json(
        "POST",
        f"{base}/api/user/login",
        payload={"username": args.username, "password": args.password},
        timeout=args.timeout,
    )
    check_business_success(status, payload, "登录")
    token = payload.get("data", {}).get("access_token")
    assert_true(bool(token), "登录成功但未返回 access_token")

    print("[2/6] 校验 /api/user/me ...")
    status, payload = request_json("GET", f"{base}/api/user/me", token=token, timeout=args.timeout)
    check_business_success(status, payload, "/api/user/me")
    data = payload.get("data", {})
    assert_true(data.get("username") == args.username, f"/api/user/me 用户名不匹配: {data.get('username')}")
    assert_true(isinstance(data.get("roles"), list), "/api/user/me roles 不是列表")
    assert_true(isinstance(data.get("permissions"), list), "/api/user/me permissions 不是列表")

    print("[3/6] 校验 RBAC 角色列表接口 ...")
    status, payload = request_json("GET", f"{base}/api/rbac/roles", token=token, timeout=args.timeout)
    check_business_success(status, payload, "/api/rbac/roles")
    assert_true(isinstance(payload.get("data"), list), "/api/rbac/roles data 不是列表")

    print("[4/6] 校验无 token 时 RBAC 受保护 ...")
    status, payload = request_json("GET", f"{base}/api/rbac/roles", timeout=args.timeout)
    assert_true(status in (401, 403), f"无 token 访问 /api/rbac/roles 应返回 401/403，实际 {status}, body={payload}")

    protected_checks = [
        ("GET", "/api/student/query?page=1&page_size=5", None),
        ("GET", "/api/score/query?page=1&page_size=5", None),
        ("GET", "/api/class/query?page=1&page_size=5", None),
        ("GET", "/api/course/query?page=1&page_size=5", None),
        ("GET", "/api/employment/query?page=1&page_size=5", None),
        ("GET", "/api/class-teaching/query?page=1&page_size=5", None),
    ]

    print("[5/6] 校验受保护业务接口可访问（当前账号）...")
    for method, path, body in protected_checks:
        url = f"{base}{path}"
        status, payload = request_json(method, url, payload=body, token=token, timeout=args.timeout)
        check_business_success(status, payload, path)

    print("[6/6] RBAC 冒烟测试通过")
    print("PASS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
