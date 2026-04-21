import { useState } from "react";
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
  Switch,
  Table,
  Typography,
  message,
} from "antd";

import { queryClient } from "../lib/queryClient";
import {
  addClassTeaching,
  deleteClassTeaching,
  queryClassTeaching,
  queryClassTeachingByCondition,
  updateClassTeaching,
} from "../services/classTeaching";
import type { ClassTeachingItem } from "../types/modules";

function pseudoTotal(page: number, pageSize: number, len: number) {
  return len < pageSize ? (page - 1) * pageSize + len : page * pageSize + 1;
}

export function ClassTeachingPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState<Record<string, unknown> | null>(null);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(false);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();

  const { data = [], isLoading } = useQuery({
    queryKey: ["teaching", page, pageSize, filters],
    queryFn: () =>
      filters
        ? queryClassTeachingByCondition({ page, page_size: pageSize, ...filters })
        : queryClassTeaching({ page, page_size: pageSize }),
  });

  const saveMutation = useMutation({
    mutationFn: async (payload: Record<string, unknown>) =>
      editing ? updateClassTeaching(payload) : addClassTeaching(payload),
    onSuccess: () => {
      message.success(editing ? "更新成功" : "新增成功");
      setOpen(false);
      queryClient.invalidateQueries({ queryKey: ["teaching"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteClassTeaching,
    onSuccess: () => {
      message.success("删除成功");
      queryClient.invalidateQueries({ queryKey: ["teaching"] });
    },
  });

  return (
    <Card
      title={<Typography.Title level={5} style={{ margin: 0 }}>班级授课管理</Typography.Title>}
      extra={
        <Space>
          <Button onClick={() => { setEditing(true); form.resetFields(); setOpen(true); }}>按ID更新</Button>
          <Button type="primary" onClick={() => { setEditing(false); form.resetFields(); setOpen(true); }}>新增授课</Button>
        </Space>
      }
    >
      <Form form={searchForm} layout="inline" onFinish={(values) => { setPage(1); setFilters(values); }}>
        <Form.Item name="class_code" label="班级编号"><Input allowClear /></Form.Item>
        <Form.Item name="lecturer_code" label="讲师编号"><Input allowClear /></Form.Item>
        <Form.Item name="course_code" label="课程编号"><Input allowClear /></Form.Item>
        <Form.Item name="is_current_teaching" label="当前授课" valuePropName="checked"><Switch /></Form.Item>
        <Form.Item><Button htmlType="submit" type="primary">查询</Button></Form.Item>
        <Form.Item><Button onClick={() => { searchForm.resetFields(); setFilters(null); setPage(1); }}>重置</Button></Form.Item>
      </Form>

      <Table<ClassTeachingItem>
        style={{ marginTop: 16 }}
        rowKey={(r) => `${r.class_code}-${r.lecturer_code}-${r.course_code}-${r.start_date}`}
        loading={isLoading}
        pagination={false}
        dataSource={data}
        columns={[
          { title: "班级", dataIndex: "class_code" },
          { title: "讲师编号", dataIndex: "lecturer_code" },
          { title: "讲师姓名", dataIndex: "lecturer_name" },
          { title: "课程编号", dataIndex: "course_code" },
          { title: "课程名称", dataIndex: "course_name" },
          { title: "开始日期", dataIndex: "start_date" },
          { title: "结束日期", dataIndex: "end_date" },
          { title: "当前授课", dataIndex: "is_current_teaching", render: (v: boolean) => (v ? "是" : "否") },
          {
            title: "删除",
            render: () => (
              <Popconfirm
                title="请输入要删除的 teaching_id"
                onConfirm={() => {
                  const input = window.prompt("请输入 teaching_id");
                  if (!input) {
                    return;
                  }
                  deleteMutation.mutate(Number(input));
                }}
              >
                <Button type="link" danger>按ID删除</Button>
              </Popconfirm>
            ),
          },
        ]}
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

      <Modal title={editing ? "按ID更新授课" : "新增授课"} open={open} onCancel={() => setOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={(values) => saveMutation.mutate(values)}>
          {editing ? <Form.Item name="id" label="授课记录ID" rules={[{ required: true }]}><InputNumber style={{ width: "100%" }} min={1} /></Form.Item> : null}
          <Form.Item name="class_code" label="班级编号" rules={[{ required: !editing }]}><Input /></Form.Item>
          <Form.Item name="lecturer_code" label="讲师编号" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="course_code" label="课程编号" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="start_date" label="开始日期(YYYY-MM-DD)" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="end_date" label="结束日期(YYYY-MM-DD)"><Input /></Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
