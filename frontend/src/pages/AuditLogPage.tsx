import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Button,
  Card,
  Col,
  DatePicker,
  Form,
  Input,
  InputNumber,
  Row,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from "antd";

import { listAuditLogs } from "../services/rbac";
import type { AuditLogItem } from "../types/rbac";

const { RangePicker } = DatePicker;

export function AuditLogPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [filters, setFilters] = useState<{
    module?: string;
    action?: string;
    operator_id?: number;
    target_type?: string;
    target_id?: string;
    start_time?: string;
    end_time?: string;
  }>({});
  const [searchForm] = Form.useForm();

  const { data, isLoading } = useQuery({
    queryKey: ["audit-logs", page, pageSize, filters],
    queryFn: () =>
      listAuditLogs({
        page,
        page_size: pageSize,
        ...filters,
      }),
  });

  const columns = useMemo(
    () => [
      { title: "ID", dataIndex: "id", key: "id", width: 80 },
      {
        title: "模块",
        dataIndex: "module",
        key: "module",
        width: 120,
        render: (v: string) => <Tag color="blue">{v}</Tag>,
      },
      {
        title: "操作",
        dataIndex: "action",
        key: "action",
        width: 180,
        render: (v: string) => <Tag color="green">{v}</Tag>,
      },
      {
        title: "操作者",
        dataIndex: "operator_username",
        key: "operator_username",
        width: 120,
      },
      {
        title: "目标类型",
        dataIndex: "target_type",
        key: "target_type",
        width: 120,
      },
      {
        title: "目标ID",
        dataIndex: "target_id",
        key: "target_id",
        width: 100,
      },
      {
        title: "时间",
        dataIndex: "created_at",
        key: "created_at",
        width: 180,
      },
    ],
    []
  );

  return (
    <Card title={<Typography.Title level={5} style={{ margin: 0 }}>审计日志</Typography.Title>}>
      <Card type="inner" title="搜索过滤" style={{ marginBottom: 16 }}>
        <Form
          form={searchForm}
          layout="inline"
          onFinish={(values) => {
            const dateRange = values.date_range;
            setFilters({
              module: values.module || undefined,
              action: values.action || undefined,
              operator_id: values.operator_id,
              target_type: values.target_type || undefined,
              target_id: values.target_id || undefined,
              start_time: dateRange?.[0]?.format("YYYY-MM-DD HH:mm:ss"),
              end_time: dateRange?.[1]?.format("YYYY-MM-DD HH:mm:ss"),
            });
            setPage(1);
          }}
        >
          <Row gutter={16} style={{ width: "100%" }}>
            <Col span={6}>
              <Form.Item name="module" label="模块">
                <Input placeholder="例如：rbac" allowClear />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="action" label="操作">
                <Input placeholder="例如：role.create" allowClear />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="operator_id" label="操作者ID">
                <InputNumber min={1} style={{ width: "100%" }} placeholder="用户ID" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="target_type" label="目标类型">
                <Input placeholder="例如：role" allowClear />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="target_id" label="目标ID">
                <Input placeholder="目标标识" allowClear />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="date_range" label="时间范围">
                <RangePicker showTime style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit">
                    搜索
                  </Button>
                  <Button
                    onClick={() => {
                      searchForm.resetFields();
                      setFilters({});
                      setPage(1);
                    }}
                  >
                    重置
                  </Button>
                </Space>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      <Table
        rowKey="id"
        loading={isLoading}
        dataSource={data?.records ?? []}
        columns={columns}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: data?.total ?? 0,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (p, ps) => {
            setPage(p);
            setPageSize(ps);
          },
        }}
      />
    </Card>
  );
}
