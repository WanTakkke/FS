import { queryClasses } from "./class";
import { queryClassTeaching } from "./classTeaching";
import { queryCourses } from "./course";
import { queryEmployments } from "./employment";
import { queryScores } from "./score";
import { queryStudents } from "./student";

export interface DashboardData {
  totalStudents: number;
  totalClasses: number;
  totalCourses: number;
  totalTeaching: number;
  totalEmployment: number;
  avgScore: number;
  scoreDistribution: Array<{ name: string; value: number }>;
}

export async function getDashboardData(): Promise<DashboardData> {
  const [students, classes, courses, teaching, employments, scores] = await Promise.all([
    queryStudents({ page: 1, page_size: 200 }),
    queryClasses({ page: 1, page_size: 200 }),
    queryCourses({ page: 1, page_size: 200 }),
    queryClassTeaching({ page: 1, page_size: 200 }),
    queryEmployments({ page: 1, page_size: 200 }),
    queryScores({ page: 1, page_size: 500 }),
  ]);

  const avgScore =
    scores.length === 0
      ? 0
      : Number((scores.reduce((sum, item) => sum + item.score, 0) / scores.length).toFixed(2));

  const scoreDistribution = [
    { name: "90-100", value: scores.filter((s) => s.score >= 90).length },
    { name: "80-89", value: scores.filter((s) => s.score >= 80 && s.score < 90).length },
    { name: "70-79", value: scores.filter((s) => s.score >= 70 && s.score < 80).length },
    { name: "<70", value: scores.filter((s) => s.score < 70).length },
  ];

  return {
    totalStudents: students.length,
    totalClasses: classes.length,
    totalCourses: courses.length,
    totalTeaching: teaching.length,
    totalEmployment: employments.length,
    avgScore,
    scoreDistribution,
  };
}
