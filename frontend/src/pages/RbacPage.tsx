import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, Col, Form, Input, InputNumber, Row, Table, Tabs, Tag, Typography } from "antd";

import {
  bindRolePermissions,
  bindUserRoles,
  createRole,
  deleteRole,
  listPermissions,
  listRoles,
  queryUserRolePermission,
  updateRole,
} from "../services/rbac";

export function RbacPage() {
  const [createForm] = Form.useForm();
  const [updateForm] = Form.useForm();
  const [bindUserRoleForm] = Form.useForm();
  const [bindRolePermissionForm] = Form.useForm();
  const [userPermissionForm] = Form.useForm();
  const [targetUserId, setTargetUserId] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const rolesQuery = useQuery({
    queryKey: ["rbac", "roles"],
    queryFn: listRoles,
  });

  const permissionsQuery = useQuery({
    queryKey: ["rbac", "permissions"],
    queryFn: listPermissions,
  });

  const userPermissionQuery = useQuery({
    queryKey: ["rbac", "user-permissions", targetUserId],
    queryFn: () => queryUserRolePermission(targetUserId as number),
    enabled: targetUserId !== null,
  });

  const createRoleMutation = useMutation({
    mutationFn: createRole,
    onSuccess: async () => {
      createForm.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["rbac", "roles"] });
    },
  });

  const updateRoleMutation = useMutation({
    mutationFn: updateRole,
    onSuccess: async () => {
      updateForm.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["rbac", "roles"] });
    },
  });

  const deleteRoleMutation = useMutation({
    mutationFn: deleteRole,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["rbac", "roles"] });
    },
  });

  const bindUserRoleMutation = useMutation({
    mutationFn: bindUserRoles,
    onSuccess: () => bindUserRoleForm.resetFields(),
  });

  const bindRolePermissionMutation = useMutation({
    mutationFn: bindRolePermissions,
    onSuccess: () => bindRolePermissionForm.resetFields(),
  });

  return (
    <Card title={<Typography.Title level={5} style={{ margin: 0 }}>RBAC 管理</Typography.Title>}>
      <Tabs
        items={[
          {
            key: "roles",
            label: "角色管理",
            children: (
              <>
                <Row gutter={16}>
                  <Col span={12}>
                    <Card type="inner" title="创建角色">
                      <Form
                        form={createForm}
                        layout="vertical"
                        onFinish={(values: { name: string; code: string; description?: string }) =>
                          createRoleMutation.mutate(values)
                        }
                      >
                        <Form.Item name="name" label="角色名称" rules={[{ required: true, message: "请输入角色名称" }]}>
                          <Input />
                        </Form.Item>
                        <Form.Item name="code" label="角色编码" rules={[{ required: true, message: "请输入角色编码" }]}>
                          <Input placeholder="例如: auditor" />
                        </Form.Item>
                        <Form.Item name="description" label="描述">
                          <Input />
                        </Form.Item>
                        <Button htmlType="submit" type="primary" loading={createRoleMutation.isPending}>
                          创建
                        </Button>
                      </Form>
                    </Card>
                  </Col>
                  <Col span={12}>
                    <Card type="inner" title="更新角色">
                      <Form
                        form={updateForm}
                        layout="vertical"
                        onFinish={(values: { role_id: number; name?: string; description?: string }) =>
                          updateRoleMutation.mutate(values)
                        }
                      >
                        <Form.Item name="role_id" label="角色ID" rules={[{ required: true, message: "请输入角色ID" }]}>
                          <InputNumber min={1} style={{ width: "100%" }} />
                        </Form.Item>
                        <Form.Item name="name" label="角色名称">
                          <Input />
                        </Form.Item>
                        <Form.Item name="description" label="描述">
                          <Input />
                        </Form.Item>
                        <Button htmlType="submit" type="primary" loading={updateRoleMutation.isPending}>
                          更新
                        </Button>
                      </Form>
                    </Card>
                  </Col>
                </Row>
                <Card type="inner" title="角色列表" style={{ marginTop: 16 }}>
                  <Table
                    rowKey="id"
                    loading={rolesQuery.isLoading}
                    dataSource={rolesQuery.data ?? []}
                    columns={[
                      { title: "ID", dataIndex: "id", key: "id", width: 80 },
                      { title: "名称", dataIndex: "name", key: "name" },
                      { title: "编码", dataIndex: "code", key: "code" },
                      { title: "描述", dataIndex: "description", key: "description" },
                      {
                        title: "操作",
                        key: "action",
                        render: (_, record: { id: number }) => (
                          <Button
                            danger
                            size="small"
                            loading={deleteRoleMutation.isPending}
                            onClick={() => deleteRoleMutation.mutate(record.id)}
                          >
                            删除
                          </Button>
                        ),
                      },
                    ]}
                  />
                </Card>
              </>
            ),
          },
          {
            key: "permissions",
            label: "权限列表",
            children: (
              <Card type="inner" title="权限点">
                <Table
                  rowKey="id"
                  loading={permissionsQuery.isLoading}
                  dataSource={permissionsQuery.data ?? []}
                  columns={[
                    { title: "ID", dataIndex: "id", key: "id", width: 80 },
                    { title: "名称", dataIndex: "name", key: "name" },
                    { title: "编码", dataIndex: "code", key: "code" },
                    { title: "类型", dataIndex: "type", key: "type", render: (v: string) => <Tag>{v}</Tag> },
                    { title: "父节点", dataIndex: "parent_id", key: "parent_id" },
                  ]}
                />
              </Card>
            ),
          },
          {
            key: "bind",
            label: "授权绑定",
            children: (
              <Row gutter={16}>
                <Col span={12}>
                  <Card type="inner" title="用户绑定角色">
                    <Form
                      form={bindUserRoleForm}
                      layout="vertical"
                      onFinish={(values: { user_id: number; role_ids_raw: string }) =>
                        bindUserRoleMutation.mutate({
                          user_id: values.user_id,
                          role_ids: values.role_ids_raw
                            .split(",")
                            .map((x) => Number(x.trim()))
                            .filter((x) => Number.isInteger(x) && x > 0),
                        })
                      }
                    >
                      <Form.Item name="user_id" label="用户ID" rules={[{ required: true, message: "请输入用户ID" }]}>
                        <InputNumber min={1} style={{ width: "100%" }} />
                      </Form.Item>
                      <Form.Item
                        name="role_ids_raw"
                        label="角色ID列表(逗号分隔)"
                        rules={[{ required: true, message: "请输入角色ID列表" }]}
                      >
                        <Input placeholder="例如: 1,2" />
                      </Form.Item>
                      <Button htmlType="submit" type="primary" loading={bindUserRoleMutation.isPending}>
                        提交
                      </Button>
                    </Form>
                  </Card>
                </Col>
                <Col span={12}>
                  <Card type="inner" title="角色绑定权限">
                    <Form
                      form={bindRolePermissionForm}
                      layout="vertical"
                      onFinish={(values: { role_id: number; permission_ids_raw: string }) =>
                        bindRolePermissionMutation.mutate({
                          role_id: values.role_id,
                          permission_ids: values.permission_ids_raw
                            .split(",")
                            .map((x) => Number(x.trim()))
                            .filter((x) => Number.isInteger(x) && x > 0),
                        })
                      }
                    >
                      <Form.Item name="role_id" label="角色ID" rules={[{ required: true, message: "请输入角色ID" }]}>
                        <InputNumber min={1} style={{ width: "100%" }} />
                      </Form.Item>
                      <Form.Item
                        name="permission_ids_raw"
                        label="权限ID列表(逗号分隔)"
                        rules={[{ required: true, message: "请输入权限ID列表" }]}
                      >
                        <Input placeholder="例如: 10,11,12" />
                      </Form.Item>
                      <Button htmlType="submit" type="primary" loading={bindRolePermissionMutation.isPending}>
                        提交
                      </Button>
                    </Form>
                  </Card>
                </Col>
              </Row>
            ),
          },
          {
            key: "user-permissions",
            label: "用户权限查询",
            children: (
              <Card type="inner" title="查询指定用户角色与权限">
                <Form
                  form={userPermissionForm}
                  layout="inline"
                  onFinish={(values: { user_id: number }) => setTargetUserId(values.user_id)}
                >
                  <Form.Item name="user_id" label="用户ID" rules={[{ required: true, message: "请输入用户ID" }]}>
                    <InputNumber min={1} />
                  </Form.Item>
                  <Button htmlType="submit" type="primary">
                    查询
                  </Button>
                </Form>
                <Card style={{ marginTop: 16 }}>
                  <Typography.Paragraph>
                    <b>用户名：</b>
                    {userPermissionQuery.data?.username ?? "-"}
                  </Typography.Paragraph>
                  <Typography.Paragraph>
                    <b>角色：</b>
                    {(userPermissionQuery.data?.roles ?? []).join(", ") || "-"}
                  </Typography.Paragraph>
                  <Typography.Paragraph>
                    <b>权限：</b>
                    {(userPermissionQuery.data?.permissions ?? []).join(", ") || "-"}
                  </Typography.Paragraph>
                </Card>
              </Card>
            ),
          },
        ]}
      />
    </Card>
  );
}
