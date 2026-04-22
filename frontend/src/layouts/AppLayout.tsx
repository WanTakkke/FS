import { Link, Outlet, useLocation } from "react-router-dom";
import { Layout, Menu, Spin, Typography } from "antd";
import {
  ApartmentOutlined,
  BarChartOutlined,
  BookOutlined,
  LogoutOutlined,
  DashboardOutlined,
  FileTextOutlined,
  SafetyCertificateOutlined,
  RobotOutlined,
  TeamOutlined,
  TrophyOutlined,
} from "@ant-design/icons";
import { Button, Space } from "antd";

import { useUiStore } from "../store/uiStore";
import { useAuthStore } from "../store/authStore";

const { Header, Content, Sider } = Layout;

const menuItems = [
  { key: "/", label: <Link to="/">概览看板</Link>, icon: <DashboardOutlined /> },
  { key: "/students", label: <Link to="/students">学生管理</Link>, icon: <TeamOutlined /> },
  { key: "/classes", label: <Link to="/classes">班级管理</Link>, icon: <ApartmentOutlined /> },
  { key: "/scores", label: <Link to="/scores">成绩管理</Link>, icon: <TrophyOutlined /> },
  { key: "/employment", label: <Link to="/employment">就业管理</Link>, icon: <BarChartOutlined /> },
  { key: "/teaching", label: <Link to="/teaching">班级授课</Link>, icon: <FileTextOutlined /> },
  { key: "/courses", label: <Link to="/courses">课程管理</Link>, icon: <BookOutlined /> },
  { key: "/ai", label: <Link to="/ai">AI 助手</Link>, icon: <RobotOutlined /> },
  { key: "/rbac", label: <Link to="/rbac">RBAC 管理</Link>, icon: <SafetyCertificateOutlined /> },
];

export function AppLayout() {
  const { pathname } = useLocation();
  const pendingRequests = useUiStore((state) => state.pendingRequests);
  const currentUser = useAuthStore((state) => state.currentUser);
  const logout = useAuthStore((state) => state.logout);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div style={{ color: "#fff", padding: 16, fontWeight: 700 }}>教学管理系统</div>
        <Menu
          mode="inline"
          theme="dark"
          selectedKeys={[pathname]}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header style={{ background: "#fff", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <Typography.Title level={4} style={{ margin: 0 }}>前端业务控制台</Typography.Title>
          <Space>
            <Typography.Text type="secondary">
              当前用户：{currentUser?.username ?? "未知"}
            </Typography.Text>
            <Spin spinning={pendingRequests > 0} size="small" />
            <Button
              icon={<LogoutOutlined />}
              onClick={() => {
                logout();
                window.location.href = "/login";
              }}
            >
              退出登录
            </Button>
          </Space>
        </Header>
        <Content style={{ margin: 16 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
