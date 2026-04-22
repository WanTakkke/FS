import { useMutation } from "@tanstack/react-query";
import { Button, Card, Form, Input, InputNumber, Table, Tabs, Typography } from "antd";

import { chatWithAi, text2sql } from "../services/ai";

export function AiPage() {
  const [chatForm] = Form.useForm();
  const [chatResultForm] = Form.useForm();
  const [text2SqlForm] = Form.useForm();
  const [text2SqlResultForm] = Form.useForm();

  const chatMutation = useMutation({
    mutationFn: chatWithAi,
    onSuccess: (res) => {
      chatResultForm.setFieldsValue({
        model: res.model,
        answer: res.answer,
      });
    },
  });

  const text2SqlMutation = useMutation({
    mutationFn: text2sql,
    onSuccess: (res) => {
      text2SqlResultForm.setFieldsValue({
        model: "",
        sql: res.sql,
        warning: res.warning ?? "",
        row_count: res.row_count,
      });
    },
  });

  const rows = (text2SqlMutation.data?.rows ?? []).map((item, index) => ({
    ...item,
    __rowKey: `${index}-${JSON.stringify(item)}`,
  }));
  const columns = (text2SqlMutation.data?.columns ?? []).map((key) => ({
    title: key,
    dataIndex: key,
    key,
  }));

  return (
    <Tabs
      items={[
        {
          key: "chat",
          label: "AI 对话",
          children: (
            <Card title={<Typography.Title level={5} style={{ margin: 0 }}>AI 对话</Typography.Title>}>
              <Form
                form={chatForm}
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
                <Form form={chatResultForm} layout="vertical">
                  <Form.Item name="model" label="返回模型"><Input readOnly /></Form.Item>
                  <Form.Item name="answer" label="回答"><Input.TextArea rows={8} readOnly /></Form.Item>
                </Form>
              </Card>
            </Card>
          ),
        },
        {
          key: "text2sql",
          label: "Text2SQL",
          children: (
            <Card title={<Typography.Title level={5} style={{ margin: 0 }}>Text2SQL 查询</Typography.Title>}>
              <Form
                form={text2SqlForm}
                layout="vertical"
                onFinish={(values) => text2SqlMutation.mutate(values)}
              >
                <Form.Item name="question" label="自然语言问题" rules={[{ required: true, message: "请输入查询问题" }]}>
                  <Input.TextArea rows={3} placeholder="例如：查询最近30天就业薪资最高的10名学生及班级" />
                </Form.Item>
                <Form.Item name="model" label="模型(可选，不填走后端默认AI_MODEL)">
                  <Input placeholder="qwen3-max" />
                </Form.Item>
                <Form.Item name="temperature" label="温度" initialValue={0}>
                  <InputNumber style={{ width: 220 }} min={0} max={1} step={0.1} />
                </Form.Item>
                <Form.Item name="max_rows" label="最大返回行数" initialValue={100}>
                  <InputNumber style={{ width: 220 }} min={1} max={200} />
                </Form.Item>
                <Button htmlType="submit" type="primary" loading={text2SqlMutation.isPending}>生成并执行</Button>
              </Form>

              <Card style={{ marginTop: 16 }} type="inner" title="SQL 与执行信息">
                <Form form={text2SqlResultForm} layout="vertical">
                  <Form.Item name="sql" label="生成 SQL"><Input.TextArea rows={4} readOnly /></Form.Item>
                  <Form.Item name="warning" label="警告"><Input readOnly /></Form.Item>
                  <Form.Item name="row_count" label="返回行数"><Input readOnly /></Form.Item>
                </Form>
              </Card>

              <Card style={{ marginTop: 16 }} type="inner" title="查询结果">
                <Table
                  rowKey="__rowKey"
                  columns={columns}
                  dataSource={rows}
                  pagination={{ pageSize: 10 }}
                  scroll={{ x: true }}
                />
              </Card>
            </Card>
          ),
        },
      ]}
    />
  );
}
