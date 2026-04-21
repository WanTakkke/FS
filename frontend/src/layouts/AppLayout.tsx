import { Link, Outlet, useLocation } from "react-router-dom";
import { Layout, Menu, Spin, Typography } from "antd";
import {
  ApartmentOutlined,
  BarChartOutlined,
  BookOutlined,
  DashboardOutlined,
  FileTextOutlined,
  RobotOutlined,
  TeamOutlined,
  TrophyOutlined,
} from "@ant-design/icons";

import { useUiStore } from "../store/uiStore";

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
];

export function AppLayout() {
  const { pathname } = useLocation();
  const pendingRequests = useUiStore((state) => state.pendingRequests);

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
          <Spin spinning={pendingRequests > 0} size="small" />
        </Header>
        <Content style={{ margin: 16 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
