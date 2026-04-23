import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Select,
  Space,
  Table,
  Tag,
  Typography,
  message,
} from "antd";

import { queryClient } from "../lib/queryClient";
import {
  deleteUser,
  listUsers,
  resetUserPassword,
  updateUser,
  updateUserStatus,
} from "../services/auth";
import type { User } from "../types/rbac";

export function UserPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState<{
    username?: string;
    email?: string;
    is_active?: number;
  }>({});
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [passwordModalOpen, setPasswordModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [editForm] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [searchForm] = Form.useForm();

  const { data, isLoading } = useQuery({
    queryKey: ["users", page, pageSize, filters],
    queryFn: () =>
      listUsers({
        page,
        page_size: pageSize,
        ...filters,
      }),
  });

  const updateMutation = useMutation({
    mutationFn: (payload: { userId: number; email?: string }) =>
      updateUser(payload.userId, { email: payload.email }),
    onSuccess: () => {
      message.success("更新成功");
      setEditModalOpen(false);
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const statusMutation = useMutation({
    mutationFn: (payload: { userId: number; is_active: number }) =>
      updateUserStatus(payload.userId, { is_active: payload.is_active }),
    onSuccess: () => {
      message.success("状态更新成功");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const resetPasswordMutation = useMutation({
    mutationFn: (payload: { userId: number; new_password: string }) =>
      resetUserPassword(payload.userId, { new_password: payload.new_password }),
    onSuccess: () => {
      message.success("密码重置成功");
      setPasswordModalOpen(false);
      passwordForm.resetFields();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteUser,
    onSuccess: () => {
      message.success("删除成功");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const columns = useMemo(
    () => [
      { title: "ID", dataIndex: "id", key: "id", width: 80 },
      { title: "用户名", dataIndex: "username", key: "username" },
      { title: "邮箱", dataIndex: "email", key: "email" },
      {
        title: "状态",
        dataIndex: "is_active",
        key: "is_active",
        width: 100,
        render: (v: number) =>
          v === 1 ? <Tag color="green">启用</Tag> : <Tag color="red">禁用</Tag>,
      },
      {
        title: "创建时间",
        dataIndex: "created_at",
        key: "created_at",
        width: 180,
      },
      {
        title: "操作",
        key: "action",
        width: 280,
        render: (_: unknown, record: User) => (
          <Space>
            <Button
              type="link"
              size="small"
              onClick={() => {
                setEditingUser(record);
                editForm.setFieldsValue({ email: record.email });
                setEditModalOpen(true);
              }}
            >
              编辑
            </Button>
            <Button
              type="link"
              size="small"
              onClick={() => {
                setEditingUser(record);
                setPasswordModalOpen(true);
              }}
            >
              重置密码
            </Button>
            <Button
              type="link"
              size="small"
              onClick={() => {
                statusMutation.mutate({
                  userId: record.id,
                  is_active: record.is_active === 1 ? 0 : 1,
                });
              }}
              loading={statusMutation.isPending}
            >
              {record.is_active === 1 ? "禁用" : "启用"}
            </Button>
            <Popconfirm
              title="确定删除该用户吗？"
              onConfirm={() => deleteMutation.mutate(record.id)}
            >
              <Button type="link" danger size="small" loading={deleteMutation.isPending}>
                删除
              </Button>
            </Popconfirm>
          </Space>
        ),
      },
    ],
    [deleteMutation, editForm, statusMutation]
  );

  return (
    <Card
      title={<Typography.Title level={5} style={{ margin: 0 }}>用户管理</Typography.Title>}
    >
      <Card type="inner" title="搜索" style={{ marginBottom: 16 }}>
        <Form
          form={searchForm}
          layout="inline"
          onFinish={(values) => {
            setFilters({
              username: values.username || undefined,
              email: values.email || undefined,
              is_active: values.is_active,
            });
            setPage(1);
          }}
        >
          <Form.Item name="username" label="用户名">
            <Input placeholder="请输入用户名" allowClear />
          </Form.Item>
          <Form.Item name="email" label="邮箱">
            <Input placeholder="请输入邮箱" allowClear />
          </Form.Item>
          <Form.Item name="is_active" label="状态">
            <Select
              allowClear
              placeholder="请选择状态"
              style={{ width: 120 }}
              options={[
                { label: "启用", value: 1 },
                { label: "禁用", value: 0 },
              ]}
            />
          </Form.Item>
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

      <Modal
        title="编辑用户"
        open={editModalOpen}
        onCancel={() => {
          setEditModalOpen(false);
          editForm.resetFields();
        }}
        onOk={() => editForm.submit()}
        confirmLoading={updateMutation.isPending}
      >
        <Form
          form={editForm}
          layout="vertical"
          onFinish={(values) => {
            if (editingUser) {
              updateMutation.mutate({
                userId: editingUser.id,
                email: values.email,
              });
            }
          }}
        >
          <Form.Item label="用户名">
            <Input value={editingUser?.username} disabled />
          </Form.Item>
          <Form.Item name="email" label="邮箱">
            <Input placeholder="请输入邮箱" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="重置密码"
        open={passwordModalOpen}
        onCancel={() => {
          setPasswordModalOpen(false);
          passwordForm.resetFields();
        }}
        onOk={() => passwordForm.submit()}
        confirmLoading={resetPasswordMutation.isPending}
      >
        <Form
          form={passwordForm}
          layout="vertical"
          onFinish={(values) => {
            if (editingUser) {
              resetPasswordMutation.mutate({
                userId: editingUser.id,
                new_password: values.new_password,
              });
            }
          }}
        >
          <Form.Item label="用户名">
            <Input value={editingUser?.username} disabled />
          </Form.Item>
          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: "请输入新密码" },
              { min: 6, message: "密码至少6位" },
            ]}
          >
            <Input.Password placeholder="请输入新密码" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
