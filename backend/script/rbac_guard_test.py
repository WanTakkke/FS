import argparse
import json
import sys
import urllib.error
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
    assert_true(payload.get("code") == 200, f"{scene}: 业务码异常，期望 200，实际 {payload.get('code')}，message={payload.get('message')}")


def check_business_error(status: int, payload: dict, scene: str, expected_fragments: list[str]):
    assert_true(status == 200, f"{scene}: HTTP 状态码异常，期望 200，实际 {status}")
    assert_true(isinstance(payload, dict), f"{scene}: 响应不是 JSON 对象")
    code = payload.get("code")
    msg = str(payload.get("message") or "")
    assert_true(code != 200, f"{scene}: 期望业务失败，实际成功，message={msg}")
    assert_true(
        any(fragment in msg for fragment in expected_fragments),
        f"{scene}: 错误消息不符合预期，message={msg}，期望包含任一片段={expected_fragments}",
    )


def main():
    parser = argparse.ArgumentParser(description="RBAC 防锁死规则测试（失败即退出非0）")
    parser.add_argument("--base-url", default="http://localhost:8001", help="后端地址，默认 http://localhost:8001")
    parser.add_argument("--username", required=True, help="admin 用户名")
    parser.add_argument("--password", required=True, help="admin 密码")
    parser.add_argument("--timeout", type=int, default=12, help="请求超时秒数")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")

    print("[1/5] 登录获取 token ...")
    status, payload = request_json(
        "POST",
        f"{base}/api/user/login",
        payload={"username": args.username, "password": args.password},
        timeout=args.timeout,
    )
    check_business_success(status, payload, "登录")
    token = payload.get("data", {}).get("access_token")
    assert_true(bool(token), "登录成功但未返回 access_token")

    print("[2/5] 获取当前用户信息与 admin 角色ID ...")
    status, payload = request_json("GET", f"{base}/api/user/me", token=token, timeout=args.timeout)
    check_business_success(status, payload, "/api/user/me")
    me = payload.get("data", {})
    current_user_id = int(me.get("id") or 0)
    assert_true(current_user_id > 0, "当前用户ID无效")

    status, payload = request_json("GET", f"{base}/api/rbac/roles", token=token, timeout=args.timeout)
    check_business_success(status, payload, "/api/rbac/roles")
    roles = payload.get("data") or []
    admin_role = next((x for x in roles if x.get("code") == "admin"), None)
    assert_true(admin_role is not None, "未找到 admin 角色")
    admin_role_id = int(admin_role["id"])

    print("[3/5] 校验防自降权：不能移除自己的超级管理员角色 ...")
    status, payload = request_json(
        "POST",
        f"{base}/api/rbac/users/roles",
        payload={"user_id": current_user_id, "role_ids": []},
        token=token,
        timeout=args.timeout,
    )
    check_business_error(
        status,
        payload,
        "防自降权校验",
        expected_fragments=["不能移除自己的超级管理员角色", "系统至少保留1个超级管理员"],
    )

    print("[4/5] 校验防锁死：禁止删除仍有关联用户的 admin 角色 ...")
    status, payload = request_json(
        "DELETE",
        f"{base}/api/rbac/roles/{admin_role_id}",
        token=token,
        timeout=args.timeout,
    )
    check_business_error(
        status,
        payload,
        "删除admin角色保护校验",
        expected_fragments=["超级管理员角色仍有关联用户，禁止删除"],
    )

    print("[5/5] RBAC 防锁死规则测试通过")
    print("PASS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
