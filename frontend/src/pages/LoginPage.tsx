import { useMutation } from "@tanstack/react-query";
import { Button, Card, Form, Input, Typography } from "antd";
import { useNavigate } from "react-router-dom";

import { login, queryCurrentUser } from "../services/auth";
import { useAuthStore } from "../store/authStore";

export function LoginPage() {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const setTokens = useAuthStore((state) => state.setTokens);
  const setCurrentUser = useAuthStore((state) => state.setCurrentUser);

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: async (tokenData) => {
      setTokens(tokenData);
      const userInfo = await queryCurrentUser();
      setCurrentUser(userInfo);
      navigate("/", { replace: true });
    },
  });

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Card style={{ width: 420 }}>
        <Typography.Title level={4}>系统登录</Typography.Title>
        <Form
          form={form}
          layout="vertical"
          onFinish={(values: { username: string; password: string }) => loginMutation.mutate(values)}
        >
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: "请输入用户名" }]}>
            <Input autoComplete="username" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, message: "请输入密码" }]}>
            <Input.Password autoComplete="current-password" />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={loginMutation.isPending} block>
            登录
          </Button>
        </Form>
      </Card>
    </div>
  );
}
