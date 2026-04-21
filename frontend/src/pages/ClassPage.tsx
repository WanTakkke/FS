import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Button,
  Card,
  Form,
  Input,
  Modal,
  Pagination,
  Popconfirm,
  Space,
  Table,
  Typography,
  message,
} from "antd";

import { queryClient } from "../lib/queryClient";
import { addClass, deleteClass, queryClasses, queryClassesByCondition, updateClass } from "../services/class";
import type { ClassItem } from "../types/modules";

function pseudoTotal(page: number, pageSize: number, len: number) {
  return len < pageSize ? (page - 1) * pageSize + len : page * pageSize + 1;
}

export function ClassPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState<Record<string, unknown> | null>(null);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<ClassItem | null>(null);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();

  const { data = [], isLoading } = useQuery({
    queryKey: ["classes", page, pageSize, filters],
    queryFn: () =>
      filters
        ? queryClassesByCondition({ page, page_size: pageSize, ...filters })
        : queryClasses({ page, page_size: pageSize }),
  });

  const saveMutation = useMutation({
    mutationFn: async (payload: Record<string, unknown>) =>
      editing ? updateClass(payload) : addClass(payload),
    onSuccess: () => {
      message.success(editing ? "更新成功" : "新增成功");
      setOpen(false);
      queryClient.invalidateQueries({ queryKey: ["classes"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteClass,
    onSuccess: () => {
      message.success("删除成功");
      queryClient.invalidateQueries({ queryKey: ["classes"] });
    },
  });

  const columns = useMemo(
    () => [
      { title: "班级编号", dataIndex: "class_code" },
      { title: "开班日期", dataIndex: "start_date" },
      { title: "班主任", dataIndex: "homeroom_teacher" },
      {
        title: "操作",
        render: (_: unknown, record: ClassItem) => (
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
            <Popconfirm title="确定删除该班级吗？" onConfirm={() => deleteMutation.mutate(record.class_code)}>
              <Button type="link" danger>删除</Button>
            </Popconfirm>
          </Space>
        ),
      },
    ],
    [deleteMutation, form],
  );

  return (
    <Card
      title={<Typography.Title level={5} style={{ margin: 0 }}>班级管理</Typography.Title>}
      extra={<Button type="primary" onClick={() => { setEditing(null); form.resetFields(); setOpen(true); }}>新增班级</Button>}
    >
      <Form
        form={searchForm}
        layout="inline"
        onFinish={(values) => {
          setPage(1);
          setFilters(values);
        }}
      >
        <Form.Item name="class_code" label="班级编号"><Input allowClear /></Form.Item>
        <Form.Item name="homeroom_teacher" label="班主任"><Input allowClear /></Form.Item>
        <Form.Item><Button htmlType="submit" type="primary">查询</Button></Form.Item>
        <Form.Item><Button onClick={() => { searchForm.resetFields(); setFilters(null); setPage(1); }}>重置</Button></Form.Item>
      </Form>

      <Table style={{ marginTop: 16 }} rowKey="class_code" loading={isLoading} columns={columns} dataSource={data} pagination={false} />
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

      <Modal title={editing ? "编辑班级" : "新增班级"} open={open} onCancel={() => setOpen(false)} onOk={() => form.submit()}>
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => saveMutation.mutate(values)}
        >
          <Form.Item name="class_code" label="班级编号" rules={[{ required: true }]}><Input disabled={!!editing} /></Form.Item>
          <Form.Item name="start_date" label="开班日期(YYYY-MM-DD)" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="homeroom_teacher" label="班主任姓名" rules={[{ required: true }]}><Input /></Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
