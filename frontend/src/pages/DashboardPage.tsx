import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import ReactECharts from "echarts-for-react";
import { Card, Col, Row, Statistic, Typography } from "antd";

import { getDashboardData } from "../services/dashboard";

export function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: getDashboardData,
  });

  const option = useMemo(
    () => ({
      tooltip: { trigger: "item" },
      series: [
        {
          type: "pie",
          radius: "70%",
          data: data?.scoreDistribution ?? [],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: "rgba(0, 0, 0, 0.5)",
            },
          },
        },
      ],
    }),
    [data?.scoreDistribution],
  );

  return (
    <div>
      <Typography.Title level={4}>系统概览</Typography.Title>
      <Row gutter={[16, 16]}>
        <Col span={8}><Card loading={isLoading}><Statistic title="学生总数" value={data?.totalStudents ?? 0} /></Card></Col>
        <Col span={8}><Card loading={isLoading}><Statistic title="班级总数" value={data?.totalClasses ?? 0} /></Card></Col>
        <Col span={8}><Card loading={isLoading}><Statistic title="课程总数" value={data?.totalCourses ?? 0} /></Card></Col>
        <Col span={8}><Card loading={isLoading}><Statistic title="授课记录数" value={data?.totalTeaching ?? 0} /></Card></Col>
        <Col span={8}><Card loading={isLoading}><Statistic title="就业记录数" value={data?.totalEmployment ?? 0} /></Card></Col>
        <Col span={8}><Card loading={isLoading}><Statistic title="平均成绩" value={data?.avgScore ?? 0} precision={2} /></Card></Col>
      </Row>
      <Card title="成绩分布" loading={isLoading} style={{ marginTop: 16 }}>
        <ReactECharts option={option} style={{ height: 320 }} />
      </Card>
    </div>
  );
}
