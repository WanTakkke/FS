import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Button,
  Card,
  DatePicker,
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
import dayjs from "dayjs";

import { queryClient } from "../lib/queryClient";
import {
  addEmployment,
  deleteEmployment,
  queryEmployments,
  queryEmploymentsByCondition,
  updateEmployment,
} from "../services/employment";
import type { EmploymentItem } from "../types/modules";

function pseudoTotal(page: number, pageSize: number, len: number) {
  return len < pageSize ? (page - 1) * pageSize + len : page * pageSize + 1;
}

export function EmploymentPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState<Record<string, unknown> | null>(null);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(false);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();

  const { data = [], isLoading } = useQuery({
    queryKey: ["employment", page, pageSize, filters],
    queryFn: () =>
      filters
        ? queryEmploymentsByCondition({ page, page_size: pageSize, ...filters })
        : queryEmployments({ page, page_size: pageSize }),
  });

  const saveMutation = useMutation({
    mutationFn: async (payload: Record<string, unknown>) => (editing ? updateEmployment(payload) : addEmployment(payload)),
    onSuccess: () => {
      message.success(editing ? "更新成功" : "新增成功");
      setOpen(false);
      queryClient.invalidateQueries({ queryKey: ["employment"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteEmployment,
    onSuccess: () => {
      message.success("删除成功");
      queryClient.invalidateQueries({ queryKey: ["employment"] });
    },
  });

  return (
    <Card
      title={<Typography.Title level={5} style={{ margin: 0 }}>就业管理</Typography.Title>}
      extra={
        <Space>
          <Button
            onClick={() => {
              setEditing(true);
              form.resetFields();
              setOpen(true);
            }}
          >
            按ID更新
          </Button>
          <Button
            type="primary"
            onClick={() => {
              setEditing(false);
              form.resetFields();
              setOpen(true);
            }}
          >
            新增就业
          </Button>
        </Space>
      }
    >
      <Form form={searchForm} layout="inline" onFinish={(values) => { setPage(1); setFilters(values); }}>
        <Form.Item name="student_code" label="学号"><Input allowClear /></Form.Item>
        <Form.Item name="student_name" label="姓名"><Input allowClear /></Form.Item>
        <Form.Item name="company_name" label="公司"><Input allowClear /></Form.Item>
        <Form.Item name="is_latest_employment" label="是否最新" valuePropName="checked"><Switch /></Form.Item>
        <Form.Item><Button htmlType="submit" type="primary">查询</Button></Form.Item>
        <Form.Item><Button onClick={() => { searchForm.resetFields(); setFilters(null); setPage(1); }}>重置</Button></Form.Item>
      </Form>

      <Table<EmploymentItem>
        style={{ marginTop: 16 }}
        rowKey={(r) => `${r.student_code}-${r.company_name}-${r.job_open_date}`}
        loading={isLoading}
        pagination={false}
        dataSource={data}
        columns={[
          { title: "学号", dataIndex: "student_code" },
          { title: "姓名", dataIndex: "student_name" },
          { title: "班级", dataIndex: "class_code" },
          { title: "公司", dataIndex: "company_name" },
          { title: "开放时间", dataIndex: "job_open_date" },
          { title: "Offer时间", dataIndex: "offer_date" },
          { title: "薪资", dataIndex: "salary" },
          { title: "最新就业", dataIndex: "is_latest_employment", render: (v: boolean) => (v ? "是" : "否") },
          {
            title: "删除",
            render: () => (
              <Popconfirm
                title="请输入要删除的就业ID"
                onConfirm={() => {
                  const input = window.prompt("请输入 employment_id");
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

      <Modal
        title={editing ? "按ID更新就业" : "新增就业"}
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => {
            const payload: Record<string, unknown> = {
              ...values,
              job_open_date: values.job_open_date ? dayjs(values.job_open_date).toISOString() : undefined,
              offer_date: values.offer_date ? dayjs(values.offer_date).toISOString() : undefined,
            };
            saveMutation.mutate(payload);
          }}
        >
          {editing ? <Form.Item name="id" label="就业ID" rules={[{ required: true }]}><InputNumber style={{ width: "100%" }} min={1} /></Form.Item> : null}
          <Form.Item name="student_code" label="学生编号" rules={[{ required: !editing }]}><Input /></Form.Item>
          <Form.Item name="company_name" label="公司名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="job_open_date" label="就业开放时间" rules={[{ required: true }]}><DatePicker showTime style={{ width: "100%" }} /></Form.Item>
          <Form.Item name="offer_date" label="Offer时间"><DatePicker showTime style={{ width: "100%" }} /></Form.Item>
          <Form.Item name="salary" label="薪资"><InputNumber style={{ width: "100%" }} min={0} /></Form.Item>
          <Form.Item name="is_latest_employment" label="是否最新就业" valuePropName="checked"><Switch /></Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
