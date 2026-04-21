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
import { addCourse, deleteCourse, queryCourses, queryCoursesByCondition, updateCourse } from "../services/course";
import type { CourseItem } from "../types/modules";

function pseudoTotal(page: number, pageSize: number, len: number) {
  return len < pageSize ? (page - 1) * pageSize + len : page * pageSize + 1;
}

export function CoursePage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState<Record<string, unknown> | null>(null);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<CourseItem | null>(null);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();

  const { data = [], isLoading } = useQuery({
    queryKey: ["courses", page, pageSize, filters],
    queryFn: () =>
      filters
        ? queryCoursesByCondition({ page, page_size: pageSize, ...filters })
        : queryCourses({ page, page_size: pageSize }),
  });

  const saveMutation = useMutation({
    mutationFn: async (payload: Record<string, unknown>) =>
      editing ? updateCourse(payload) : addCourse(payload),
    onSuccess: () => {
      message.success(editing ? "更新成功" : "新增成功");
      setOpen(false);
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteCourse,
    onSuccess: () => {
      message.success("删除成功");
      queryClient.invalidateQueries({ queryKey: ["courses"] });
    },
  });

  const columns = useMemo(
    () => [
      { title: "课程编号", dataIndex: "course_code" },
      { title: "课程名称", dataIndex: "course_name" },
      { title: "课程描述", dataIndex: "description" },
      {
        title: "操作",
        render: (_: unknown, record: CourseItem) => (
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
            <Popconfirm title="确定删除该课程吗？" onConfirm={() => deleteMutation.mutate(record.course_code)}>
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
      title={<Typography.Title level={5} style={{ margin: 0 }}>课程管理</Typography.Title>}
      extra={<Button type="primary" onClick={() => { setEditing(null); form.resetFields(); setOpen(true); }}>新增课程</Button>}
    >
      <Form form={searchForm} layout="inline" onFinish={(values) => { setPage(1); setFilters(values); }}>
        <Form.Item name="course_code" label="课程编号"><Input allowClear /></Form.Item>
        <Form.Item name="course_name" label="课程名称"><Input allowClear /></Form.Item>
        <Form.Item><Button htmlType="submit" type="primary">查询</Button></Form.Item>
        <Form.Item><Button onClick={() => { searchForm.resetFields(); setFilters(null); setPage(1); }}>重置</Button></Form.Item>
      </Form>

      <Table style={{ marginTop: 16 }} rowKey="course_code" loading={isLoading} columns={columns} dataSource={data} pagination={false} />
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

      <Modal title={editing ? "编辑课程" : "新增课程"} open={open} onCancel={() => setOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={(values) => saveMutation.mutate(values)}>
          <Form.Item name="course_code" label="课程编号" rules={[{ required: true }]}><Input disabled={!!editing} /></Form.Item>
          <Form.Item name="course_name" label="课程名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="description" label="课程描述"><Input.TextArea rows={3} /></Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
