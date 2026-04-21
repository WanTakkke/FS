import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "../layouts/AppLayout";
import { AiPage } from "../pages/AiPage";
import { ClassPage } from "../pages/ClassPage";
import { ClassTeachingPage } from "../pages/ClassTeachingPage";
import { CoursePage } from "../pages/CoursePage";
import { DashboardPage } from "../pages/DashboardPage";
import { EmploymentPage } from "../pages/EmploymentPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { ScorePage } from "../pages/ScorePage";
import { StudentPage } from "../pages/StudentPage";

export function AppRouter() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/students" element={<StudentPage />} />
        <Route path="/classes" element={<ClassPage />} />
        <Route path="/scores" element={<ScorePage />} />
        <Route path="/employment" element={<EmploymentPage />} />
        <Route path="/teaching" element={<ClassTeachingPage />} />
        <Route path="/courses" element={<CoursePage />} />
        <Route path="/ai" element={<AiPage />} />
      </Route>
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
}
