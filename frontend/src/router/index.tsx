import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "../layouts/AppLayout";
import { AiPage } from "../pages/AiPage";
import { ClassPage } from "../pages/ClassPage";
import { ClassTeachingPage } from "../pages/ClassTeachingPage";
import { CoursePage } from "../pages/CoursePage";
import { DashboardPage } from "../pages/DashboardPage";
import { EmploymentPage } from "../pages/EmploymentPage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { RbacPage } from "../pages/RbacPage";
import { ScorePage } from "../pages/ScorePage";
import { StudentPage } from "../pages/StudentPage";
import { UserPage } from "../pages/UserPage";
import { useAuthStore } from "../store/authStore";

function RequireAuth({ children }: { children: ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={(
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        )}
      >
        <Route path="/" element={<DashboardPage />} />
        <Route path="/students" element={<StudentPage />} />
        <Route path="/classes" element={<ClassPage />} />
        <Route path="/scores" element={<ScorePage />} />
        <Route path="/employment" element={<EmploymentPage />} />
        <Route path="/teaching" element={<ClassTeachingPage />} />
        <Route path="/courses" element={<CoursePage />} />
        <Route path="/ai" element={<AiPage />} />
        <Route path="/rbac" element={<RbacPage />} />
        <Route path="/users" element={<UserPage />} />
      </Route>
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
}
