import { useMutation } from "@tanstack/react-query";
import { Button, Card, Form, Input, InputNumber, Typography } from "antd";

import { chatWithAi } from "../services/ai";

export function AiPage() {
  const [form] = Form.useForm();
  const [resultForm] = Form.useForm();

  const chatMutation = useMutation({
    mutationFn: chatWithAi,
    onSuccess: (res) => {
      resultForm.setFieldsValue({
        model: res.model,
        answer: res.answer,
      });
    },
  });

  return (
    <Card title={<Typography.Title level={5} style={{ margin: 0 }}>AI 助手</Typography.Title>}>
      <Form
        form={form}
        layout="vertical"
        onFinish={(values) => chatMutation.mutate(values)}
      >
        <Form.Item name="model" label="模型(可选，不填走后端默认AI_MODEL)">
          <Input placeholder="gpt-4o-mini" />
        </Form.Item>
        <Form.Item name="temperature" label="温度" initialValue={0.7}>
          <InputNumber style={{ width: 220 }} min={0} max={2} step={0.1} />
        </Form.Item>
        <Form.Item name="message" label="提问内容" rules={[{ required: true, message: "请输入内容" }]}>
          <Input.TextArea rows={4} />
        </Form.Item>
        <Button htmlType="submit" type="primary" loading={chatMutation.isPending}>发送</Button>
      </Form>

      <Card style={{ marginTop: 16 }} type="inner" title="响应结果">
        <Form form={resultForm} layout="vertical">
          <Form.Item name="model" label="返回模型"><Input readOnly /></Form.Item>
          <Form.Item name="answer" label="回答"><Input.TextArea rows={8} readOnly /></Form.Item>
        </Form>
      </Card>
    </Card>
  );
}
