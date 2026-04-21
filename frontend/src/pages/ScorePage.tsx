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
  Table,
  Typography,
  message,
} from "antd";

import { queryClient } from "../lib/queryClient";
import { addScore, deleteScore, queryScores, queryScoresByCondition, updateScore } from "../services/score";
import type { ScoreItem } from "../types/modules";

function pseudoTotal(page: number, pageSize: number, len: number) {
  return len < pageSize ? (page - 1) * pageSize + len : page * pageSize + 1;
}

export function ScorePage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState<Record<string, unknown> | null>(null);
  const [open, setOpen] = useState(false);
  const [editingKey, setEditingKey] = useState<{ student_code: string; exam_sequence: string } | null>(null);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();

  const { data = [], isLoading } = useQuery({
    queryKey: ["scores", page, pageSize, filters],
    queryFn: () =>
      filters
        ? queryScoresByCondition({ page, page_size: pageSize, ...filters })
        : queryScores({ page, page_size: pageSize }),
  });

  const saveMutation = useMutation({
    mutationFn: async (payload: Record<string, unknown>) =>
      editingKey ? updateScore(payload) : addScore(payload),
    onSuccess: () => {
      message.success(editingKey ? "更新成功" : "新增成功");
      setOpen(false);
      queryClient.invalidateQueries({ queryKey: ["scores"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: ({ studentCode, examSequence }: { studentCode: string; examSequence: string }) =>
      deleteScore(studentCode, examSequence),
    onSuccess: () => {
      message.success("删除成功");
      queryClient.invalidateQueries({ queryKey: ["scores"] });
    },
  });

  return (
    <Card
      title={<Typography.Title level={5} style={{ margin: 0 }}>成绩管理</Typography.Title>}
      extra={<Button type="primary" onClick={() => { setEditingKey(null); form.resetFields(); setOpen(true); }}>新增成绩</Button>}
    >
      <Form form={searchForm} layout="inline" onFinish={(values) => { setPage(1); setFilters(values); }}>
        <Form.Item name="student_name" label="学生姓名"><Input allowClear /></Form.Item>
        <Form.Item name="exam_sequence" label="考核序次"><Input allowClear /></Form.Item>
        <Form.Item><Button htmlType="submit" type="primary">查询</Button></Form.Item>
        <Form.Item><Button onClick={() => { searchForm.resetFields(); setFilters(null); setPage(1); }}>重置</Button></Form.Item>
      </Form>

      <Table<ScoreItem>
        style={{ marginTop: 16 }}
        rowKey={(r) => `${r.student_name}-${r.exam_sequence}-${r.class_code}`}
        loading={isLoading}
        pagination={false}
        dataSource={data}
        columns={[
          { title: "班级", dataIndex: "class_code" },
          { title: "学生姓名", dataIndex: "student_name" },
          { title: "考核序次", dataIndex: "exam_sequence" },
          { title: "成绩", dataIndex: "score" },
          {
            title: "操作",
            render: (_, record) => (
              <Space>
                <Button
                  type="link"
                  onClick={() => {
                    setEditingKey({ student_code: "", exam_sequence: record.exam_sequence });
                    form.setFieldsValue({
                      exam_sequence: record.exam_sequence,
                      score: record.score,
                    });
                    setOpen(true);
                  }}
                >
                  编辑
                </Button>
                <Popconfirm
                  title="删除需要输入学生编号和考核序次，是否继续？"
                  onConfirm={() => {
                    const studentCode = window.prompt("请输入 student_code");
                    if (!studentCode) {
                      return;
                    }
                    deleteMutation.mutate({ studentCode, examSequence: record.exam_sequence });
                  }}
                >
                  <Button type="link" danger>删除</Button>
                </Popconfirm>
              </Space>
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
        title={editingKey ? "编辑成绩(需填写学生编号)" : "新增成绩"}
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={saveMutation.isPending}
      >
        <Form form={form} layout="vertical" onFinish={(values) => saveMutation.mutate(values)}>
          <Form.Item name="student_code" label="学生编号" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="exam_sequence" label="考核序次" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="score" label="成绩" rules={[{ required: true }]}><InputNumber style={{ width: "100%" }} min={0} max={100} step={0.01} /></Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
