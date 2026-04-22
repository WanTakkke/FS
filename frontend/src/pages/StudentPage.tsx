import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Modal,
  Pagination,
  Popconfirm,
  Space,
  Table,
  Tag,
  Typography,
  message,
} from "antd";

import { queryClient } from "../lib/queryClient";
import {
  addStudent,
  deleteStudent,
  queryStudents,
  queryStudentsByCondition,
  updateStudent,
} from "../services/student";
import type { Student } from "../types/modules";

function pseudoTotal(page: number, pageSize: number, len: number) {
  return len < pageSize ? (page - 1) * pageSize + len : page * pageSize + 1;
}

export function StudentPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState<Record<string, unknown> | null>(null);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Student | null>(null);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();

  const { data = [], isLoading } = useQuery({
    queryKey: ["students", page, pageSize, filters],
    queryFn: () =>
      filters
        ? queryStudentsByCondition({ page, page_size: pageSize, ...filters })
        : queryStudents({ page, page_size: pageSize }),
  });

  const saveMutation = useMutation({
    mutationFn: async (payload: Record<string, unknown>) =>
      editing ? updateStudent(payload) : addStudent(payload),
    onSuccess: () => {
      message.success(editing ? "更新成功" : "新增成功");
      setOpen(false);
      queryClient.invalidateQueries({ queryKey: ["students"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteStudent,
    onSuccess: () => {
      message.success("删除成功");
      queryClient.invalidateQueries({ queryKey: ["students"] });
    },
  });

  const columns = useMemo(
    () => [
      { title: "学号", dataIndex: "student_code" },
      { title: "姓名", dataIndex: "name" },
      { title: "班级ID", dataIndex: "class_id" },
      {
        title: "性别",
        dataIndex: "gender",
        render: (v: number) => (v === 1 ? <Tag color="blue">男</Tag> : <Tag color="pink">女</Tag>),
      },
      { title: "年龄", dataIndex: "age" },
      { title: "专业", dataIndex: "major" },
      {
        title: "操作",
        render: (_: unknown, record: Student) => (
          <Space>
            <Button
              type="link"
              onClick={() => {
                setEditing(record);
                form.setFieldsValue(record);
                setOpen(true);
              }}
            >
              编辑
            </Button>
            <Popconfirm
              title="确定删除该学生吗？"
              onConfirm={() => deleteMutation.mutate(record.student_code)}
            >
              <Button type="link" danger loading={deleteMutation.isPending}>
                删除
              </Button>
            </Popconfirm>
          </Space>
        ),
      },
    ],
    [deleteMutation, form],
  );

  return (
    <Card
      title={<Typography.Title level={5} style={{ margin: 0 }}>学生管理</Typography.Title>}
      extra={
        <Button
          type="primary"
          onClick={() => {
            setEditing(null);
            form.resetFields();
            setOpen(true);
          }}
        >
          新增学生
        </Button>
      }
    >
      <Form
        form={searchForm}
        layout="inline"
        onFinish={(values) => {
          setPage(1);
          setFilters(values);
        }}
      >
        <Form.Item name="student_code" label="学号"><Input allowClear /></Form.Item>
        <Form.Item name="name" label="姓名"><Input allowClear /></Form.Item>
        <Form.Item name="class_id" label="班级ID"><InputNumber min={1} /></Form.Item>
        <Form.Item><Button htmlType="submit" type="primary">查询</Button></Form.Item>
        <Form.Item>
          <Button onClick={() => { searchForm.resetFields(); setFilters(null); setPage(1); }}>重置</Button>
        </Form.Item>
      </Form>

      <Table
        style={{ marginTop: 16 }}
        rowKey="student_code"
        loading={isLoading}
        columns={columns}
        dataSource={data}
        pagination={false}
      />
      <Pagination
        style={{ marginTop: 16, textAlign: "right" }}
        current={page}
        pageSize={pageSize}
        total={pseudoTotal(page, pageSize, data.length)}
        onChange={(p, ps) => {
          setPage(p);
          setPageSize(ps);
        }}
      />

      <Modal
        title={editing ? "编辑学生" : "新增学生"}
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={saveMutation.isPending}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => saveMutation.mutate(values)}
        >
          <Form.Item name="student_code" label="学号" rules={[{ required: true }]}><Input disabled={!!editing} /></Form.Item>
          <Form.Item name="name" label="姓名" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="class_id" label="班级ID" rules={[{ required: true }]}><InputNumber style={{ width: "100%" }} min={1} /></Form.Item>
          <Form.Item name="advisor_id" label="导师ID"><InputNumber style={{ width: "100%" }} min={1} /></Form.Item>
          <Form.Item name="gender" label="性别(1男2女)" rules={[{ required: true }]}><InputNumber style={{ width: "100%" }} min={1} max={2} /></Form.Item>
          <Form.Item name="age" label="年龄"><InputNumber style={{ width: "100%" }} min={1} max={100} /></Form.Item>
          <Form.Item name="major" label="专业"><Input /></Form.Item>
          <Form.Item name="hometown" label="籍贯"><Input /></Form.Item>
          <Form.Item name="graduate_school" label="毕业院校"><Input /></Form.Item>
          <Form.Item name="education_level" label="学历"><Input /></Form.Item>
          <Form.Item name="enrollment_date" label="入学日期(YYYY-MM-DD)" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="graduation_date" label="毕业日期(YYYY-MM-DD)"><Input /></Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
