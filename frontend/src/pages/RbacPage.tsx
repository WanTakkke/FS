import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Button,
  Card,
  Col,
  Form,
  Input,
  InputNumber,
  message,
  Modal,
  Popconfirm,
  Row,
  Select,
  Space,
  Table,
  Tabs,
  Tag,
  Tree,
  Typography,
} from "antd";

import { queryClient } from "../lib/queryClient";
import {
  bindRolePermissions,
  bindUserRoles,
  createPermission,
  createRole,
  deletePermission,
  deleteRole,
  getPermissionTree,
  listPermissions,
  listRoles,
  listUsers,
  queryUserRolePermission,
  updatePermission,
  updateRole,
} from "../services/rbac";
import type { Permission, PermissionTreeNode, Role, User } from "../types/rbac";

function convertToTreeData(nodes: PermissionTreeNode[]): any[] {
  return nodes.map((node) => ({
    key: node.id,
    title: (
      <Space>
        <span>{node.name}</span>
        <Tag color={node.type === "group" ? "blue" : "green"}>{node.type}</Tag>
        <span style={{ color: "#999", fontSize: 12 }}>{node.code}</span>
      </Space>
    ),
    children: node.children && node.children.length > 0 ? convertToTreeData(node.children) : undefined,
  }));
}

function flattenPermissions(nodes: PermissionTreeNode[]): Permission[] {
  const result: Permission[] = [];
  const traverse = (node: PermissionTreeNode) => {
    result.push({
      id: node.id,
      parent_id: node.parent_id,
      name: node.name,
      code: node.code,
      type: node.type,
    });
    if (node.children) {
      node.children.forEach(traverse);
    }
  };
  nodes.forEach(traverse);
  return result;
}

export function RbacPage() {
  const [activeTab, setActiveTab] = useState("user-permissions");
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const [checkedPermissionIds, setCheckedPermissionIds] = useState<number[]>([]);
  const [checkedRoleIds, setCheckedRoleIds] = useState<number[]>([]);
  
  const [createRoleModalOpen, setCreateRoleModalOpen] = useState(false);
  const [editRoleModalOpen, setEditRoleModalOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [roleForm] = Form.useForm();
  
  const [createPermModalOpen, setCreatePermModalOpen] = useState(false);
  const [editPermModalOpen, setEditPermModalOpen] = useState(false);
  const [editingPerm, setEditingPerm] = useState<Permission | null>(null);
  const [permForm] = Form.useForm();

  const rolesQuery = useQuery({
    queryKey: ["rbac", "roles"],
    queryFn: listRoles,
  });

  const permissionsQuery = useQuery({
    queryKey: ["rbac", "permissions"],
    queryFn: listPermissions,
  });

  const permissionTreeQuery = useQuery({
    queryKey: ["rbac", "permission-tree"],
    queryFn: getPermissionTree,
  });

  const usersQuery = useQuery({
    queryKey: ["users", 1, 100],
    queryFn: () => listUsers({ page: 1, page_size: 100 }),
  });

  const userPermissionQuery = useQuery({
    queryKey: ["rbac", "user-permissions", selectedUserId],
    queryFn: () => queryUserRolePermission(selectedUserId as number),
    enabled: selectedUserId !== null,
  });

  const createRoleMutation = useMutation({
    mutationFn: createRole,
    onSuccess: () => {
      message.success("角色创建成功");
      setCreateRoleModalOpen(false);
      roleForm.resetFields();
      queryClient.invalidateQueries({ queryKey: ["rbac", "roles"] });
    },
  });

  const updateRoleMutation = useMutation({
    mutationFn: updateRole,
    onSuccess: () => {
      message.success("角色更新成功");
      setEditRoleModalOpen(false);
      setEditingRole(null);
      roleForm.resetFields();
      queryClient.invalidateQueries({ queryKey: ["rbac", "roles"] });
    },
  });

  const deleteRoleMutation = useMutation({
    mutationFn: deleteRole,
    onSuccess: () => {
      message.success("角色删除成功");
      queryClient.invalidateQueries({ queryKey: ["rbac", "roles"] });
    },
  });

  const createPermMutation = useMutation({
    mutationFn: createPermission,
    onSuccess: () => {
      message.success("权限创建成功");
      setCreatePermModalOpen(false);
      permForm.resetFields();
      queryClient.invalidateQueries({ queryKey: ["rbac", "permissions"] });
      queryClient.invalidateQueries({ queryKey: ["rbac", "permission-tree"] });
    },
  });

  const updatePermMutation = useMutation({
    mutationFn: updatePermission,
    onSuccess: () => {
      message.success("权限更新成功");
      setEditPermModalOpen(false);
      setEditingPerm(null);
      permForm.resetFields();
      queryClient.invalidateQueries({ queryKey: ["rbac", "permissions"] });
      queryClient.invalidateQueries({ queryKey: ["rbac", "permission-tree"] });
    },
  });

  const deletePermMutation = useMutation({
    mutationFn: deletePermission,
    onSuccess: () => {
      message.success("权限删除成功");
      queryClient.invalidateQueries({ queryKey: ["rbac", "permissions"] });
      queryClient.invalidateQueries({ queryKey: ["rbac", "permission-tree"] });
    },
  });

  const bindUserRoleMutation = useMutation({
    mutationFn: bindUserRoles,
    onSuccess: () => {
      message.success("用户角色绑定成功");
      queryClient.invalidateQueries({ queryKey: ["rbac", "user-permissions", selectedUserId] });
    },
  });

  const bindRolePermMutation = useMutation({
    mutationFn: bindRolePermissions,
    onSuccess: () => {
      message.success("角色权限绑定成功");
    },
  });

  const treeData = useMemo(() => {
    if (permissionTreeQuery.data) {
      return convertToTreeData(permissionTreeQuery.data);
    }
    return [];
  }, [permissionTreeQuery.data]);

  const allPermissions = useMemo(() => {
    if (permissionTreeQuery.data) {
      return flattenPermissions(permissionTreeQuery.data);
    }
    return [];
  }, [permissionTreeQuery.data]);

  const userOptions = useMemo(() => {
    return (usersQuery.data?.records ?? []).map((user: User) => ({
      label: `${user.username} (ID: ${user.id})`,
      value: user.id,
    }));
  }, [usersQuery.data]);

  const roleOptions = useMemo(() => {
    return (rolesQuery.data ?? []).map((role: Role) => ({
      label: `${role.name} (${role.code})`,
      value: role.id,
    }));
  }, [rolesQuery.data]);

  const handleUserChange = (userId: number) => {
    setSelectedUserId(userId);
    if (userPermissionQuery.data) {
      const roleIds = (rolesQuery.data ?? [])
        .filter((role: Role) => userPermissionQuery.data.roles.includes(role.code))
        .map((role: Role) => role.id);
      setCheckedRoleIds(roleIds);
    }
  };

  const handleRoleChange = (roleId: number) => {
    setSelectedRoleId(roleId);
  };

  const handlePermissionCheck = (checkedKeys: any) => {
    setCheckedPermissionIds(checkedKeys as number[]);
  };

  const handleBindUserRoles = () => {
    if (selectedUserId) {
      bindUserRoleMutation.mutate({
        user_id: selectedUserId,
        role_ids: checkedRoleIds,
      });
    }
  };

  const handleBindRolePermissions = () => {
    if (selectedRoleId) {
      bindRolePermMutation.mutate({
        role_id: selectedRoleId,
        permission_ids: checkedPermissionIds,
      });
    }
  };

  const roleColumns = useMemo(
    () => [
      { title: "ID", dataIndex: "id", key: "id", width: 80 },
      { title: "名称", dataIndex: "name", key: "name" },
      { title: "编码", dataIndex: "code", key: "code" },
      { title: "描述", dataIndex: "description", key: "description" },
      {
        title: "操作",
        key: "action",
        width: 200,
        render: (_: unknown, record: Role) => (
          <Space>
            <Button
              type="link"
              size="small"
              onClick={() => {
                setEditingRole(record);
                roleForm.setFieldsValue(record);
                setEditRoleModalOpen(true);
              }}
            >
              编辑
            </Button>
            <Popconfirm
              title="确定删除该角色吗？"
              onConfirm={() => deleteRoleMutation.mutate(record.id)}
            >
              <Button type="link" danger size="small">
                删除
              </Button>
            </Popconfirm>
          </Space>
        ),
      },
    ],
    [deleteRoleMutation, roleForm]
  );

  const permColumns = useMemo(
    () => [
      { title: "ID", dataIndex: "id", key: "id", width: 80 },
      { title: "名称", dataIndex: "name", key: "name" },
      { title: "编码", dataIndex: "code", key: "code" },
      {
        title: "类型",
        dataIndex: "type",
        key: "type",
        render: (v: string) => <Tag color={v === "group" ? "blue" : "green"}>{v}</Tag>,
      },
      { title: "父节点ID", dataIndex: "parent_id", key: "parent_id", width: 100 },
      {
        title: "操作",
        key: "action",
        width: 200,
        render: (_: unknown, record: Permission) => (
          <Space>
            <Button
              type="link"
              size="small"
              onClick={() => {
                setEditingPerm(record);
                permForm.setFieldsValue({
                  ...record,
                  permission_id: record.id,
                });
                setEditPermModalOpen(true);
              }}
            >
              编辑
            </Button>
            <Popconfirm
              title="确定删除该权限吗？"
              onConfirm={() => deletePermMutation.mutate(record.id)}
            >
              <Button type="link" danger size="small">
                删除
              </Button>
            </Popconfirm>
          </Space>
        ),
      },
    ],
    [deletePermMutation, permForm]
  );

  return (
    <Card title={<Typography.Title level={5} style={{ margin: 0 }}>RBAC 权限管理</Typography.Title>}>
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: "user-permissions",
            label: "用户权限分配",
            children: (
              <Row gutter={16}>
                <Col span={8}>
                  <Card type="inner" title="选择用户">
                    <Select
                      showSearch
                      style={{ width: "100%" }}
                      placeholder="请选择用户"
                      options={userOptions}
                      value={selectedUserId}
                      onChange={handleUserChange}
                      filterOption={(input, option) =>
                        (option?.label ?? "").toLowerCase().includes(input.toLowerCase())
                      }
                    />
                    {selectedUserId && userPermissionQuery.data && (
                      <Card style={{ marginTop: 16 }} size="small">
                        <Typography.Paragraph>
                          <b>用户名：</b>{userPermissionQuery.data.username}
                        </Typography.Paragraph>
                        <Typography.Paragraph>
                          <b>当前角色：</b>
                          <br />
                          {userPermissionQuery.data.roles.map((role) => (
                            <Tag key={role} color="blue" style={{ margin: 4 }}>
                              {role}
                            </Tag>
                          ))}
                        </Typography.Paragraph>
                        <Typography.Paragraph>
                          <b>权限数量：</b>
                          {userPermissionQuery.data.permissions.length} 个
                        </Typography.Paragraph>
                      </Card>
                    )}
                  </Card>
                </Col>
                <Col span={16}>
                  <Card type="inner" title="分配角色">
                    {selectedUserId ? (
                      <>
                        <div style={{ marginBottom: 16 }}>
                          <Typography.Text type="secondary">
                            勾选角色后点击"保存"按钮完成分配
                          </Typography.Text>
                        </div>
                        <Select
                          mode="multiple"
                          style={{ width: "100%", marginBottom: 16 }}
                          placeholder="请选择角色"
                          value={checkedRoleIds}
                          onChange={setCheckedRoleIds}
                          options={roleOptions}
                        />
                        <Button
                          type="primary"
                          onClick={handleBindUserRoles}
                          loading={bindUserRoleMutation.isPending}
                        >
                          保存
                        </Button>
                      </>
                    ) : (
                      <Typography.Text type="secondary">请先选择用户</Typography.Text>
                    )}
                  </Card>
                </Col>
              </Row>
            ),
          },
          {
            key: "role-permissions",
            label: "角色权限分配",
            children: (
              <Row gutter={16}>
                <Col span={8}>
                  <Card type="inner" title="选择角色">
                    <Select
                      showSearch
                      style={{ width: "100%" }}
                      placeholder="请选择角色"
                      options={roleOptions}
                      value={selectedRoleId}
                      onChange={handleRoleChange}
                      filterOption={(input, option) =>
                        (option?.label ?? "").toLowerCase().includes(input.toLowerCase())
                      }
                    />
                  </Card>
                </Col>
                <Col span={16}>
                  <Card type="inner" title="分配权限">
                    {selectedRoleId ? (
                      <>
                        <div style={{ marginBottom: 16 }}>
                          <Typography.Text type="secondary">
                            勾选权限后点击"保存"按钮完成分配
                          </Typography.Text>
                        </div>
                        <div style={{ maxHeight: 500, overflow: "auto", marginBottom: 16 }}>
                          <Tree
                            checkable
                            checkedKeys={checkedPermissionIds}
                            onCheck={handlePermissionCheck}
                            treeData={treeData}
                            defaultExpandAll
                          />
                        </div>
                        <Button
                          type="primary"
                          onClick={handleBindRolePermissions}
                          loading={bindRolePermMutation.isPending}
                        >
                          保存
                        </Button>
                      </>
                    ) : (
                      <Typography.Text type="secondary">请先选择角色</Typography.Text>
                    )}
                  </Card>
                </Col>
              </Row>
            ),
          },
          {
            key: "roles",
            label: "角色管理",
            children: (
              <>
                <div style={{ marginBottom: 16 }}>
                  <Button type="primary" onClick={() => setCreateRoleModalOpen(true)}>
                    创建角色
                  </Button>
                </div>
                <Table
                  rowKey="id"
                  loading={rolesQuery.isLoading}
                  dataSource={rolesQuery.data ?? []}
                  columns={roleColumns}
                />
              </>
            ),
          },
          {
            key: "permissions",
            label: "权限管理",
            children: (
              <>
                <div style={{ marginBottom: 16 }}>
                  <Button type="primary" onClick={() => setCreatePermModalOpen(true)}>
                    创建权限
                  </Button>
                </div>
                <Table
                  rowKey="id"
                  loading={permissionsQuery.isLoading}
                  dataSource={permissionsQuery.data ?? []}
                  columns={permColumns}
                />
              </>
            ),
          },
        ]}
      />

      <Modal
        title="创建角色"
        open={createRoleModalOpen}
        onCancel={() => {
          setCreateRoleModalOpen(false);
          roleForm.resetFields();
        }}
        onOk={() => roleForm.submit()}
        confirmLoading={createRoleMutation.isPending}
      >
        <Form
          form={roleForm}
          layout="vertical"
          onFinish={(values) => createRoleMutation.mutate(values)}
        >
          <Form.Item name="name" label="角色名称" rules={[{ required: true }]}>
            <Input placeholder="例如：教师" />
          </Form.Item>
          <Form.Item name="code" label="角色编码" rules={[{ required: true }]}>
            <Input placeholder="例如：teacher" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="编辑角色"
        open={editRoleModalOpen}
        onCancel={() => {
          setEditRoleModalOpen(false);
          setEditingRole(null);
          roleForm.resetFields();
        }}
        onOk={() => roleForm.submit()}
        confirmLoading={updateRoleMutation.isPending}
      >
        <Form
          form={roleForm}
          layout="vertical"
          onFinish={(values) => {
            if (editingRole) {
              updateRoleMutation.mutate({
                role_id: editingRole.id,
                name: values.name,
                description: values.description,
              });
            }
          }}
        >
          <Form.Item label="角色ID">
            <Input value={editingRole?.id} disabled />
          </Form.Item>
          <Form.Item name="name" label="角色名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="创建权限"
        open={createPermModalOpen}
        onCancel={() => {
          setCreatePermModalOpen(false);
          permForm.resetFields();
        }}
        onOk={() => permForm.submit()}
        confirmLoading={createPermMutation.isPending}
      >
        <Form
          form={permForm}
          layout="vertical"
          onFinish={(values) => createPermMutation.mutate(values)}
        >
          <Form.Item name="parent_id" label="父权限ID">
            <InputNumber min={1} style={{ width: "100%" }} placeholder="留空表示顶级权限" />
          </Form.Item>
          <Form.Item name="name" label="权限名称" rules={[{ required: true }]}>
            <Input placeholder="例如：学生查询" />
          </Form.Item>
          <Form.Item name="code" label="权限编码" rules={[{ required: true }]}>
            <Input placeholder="例如：student:read" />
          </Form.Item>
          <Form.Item name="type" label="类型" initialValue="api">
            <Select
              options={[
                { label: "API权限", value: "api" },
                { label: "权限组", value: "group" },
                { label: "菜单", value: "menu" },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="编辑权限"
        open={editPermModalOpen}
        onCancel={() => {
          setEditPermModalOpen(false);
          setEditingPerm(null);
          permForm.resetFields();
        }}
        onOk={() => permForm.submit()}
        confirmLoading={updatePermMutation.isPending}
      >
        <Form
          form={permForm}
          layout="vertical"
          onFinish={(values) => {
            if (editingPerm) {
              updatePermMutation.mutate({
                permission_id: editingPerm.id,
                parent_id: values.parent_id,
                name: values.name,
                type: values.type,
              });
            }
          }}
        >
          <Form.Item label="权限ID">
            <Input value={editingPerm?.id} disabled />
          </Form.Item>
          <Form.Item label="权限编码">
            <Input value={editingPerm?.code} disabled />
          </Form.Item>
          <Form.Item name="parent_id" label="父权限ID">
            <InputNumber min={1} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="name" label="权限名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="type" label="类型">
            <Select
              options={[
                { label: "API权限", value: "api" },
                { label: "权限组", value: "group" },
                { label: "菜单", value: "menu" },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
