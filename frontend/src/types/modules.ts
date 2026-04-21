export interface Student {
  student_code: string;
  class_id: number;
  advisor_id: number;
  name: string;
  gender: number;
  age: number;
  hometown: string;
  graduate_school: string;
  major: string;
  enrollment_date: string;
  graduation_date?: string | null;
  education_level?: string | null;
}

export interface ClassItem {
  class_code: string;
  start_date: string;
  homeroom_teacher?: string | null;
}

export interface ScoreItem {
  class_code?: string | null;
  student_name?: string | null;
  exam_sequence: string;
  score: number;
}

export interface EmploymentItem {
  student_code?: string | null;
  student_name?: string | null;
  class_code?: string | null;
  company_name: string;
  job_open_date: string;
  offer_date?: string | null;
  salary?: number | null;
  is_latest_employment: boolean;
}

export interface ClassTeachingItem {
  class_code?: string | null;
  lecturer_code?: string | null;
  lecturer_name?: string | null;
  course_code?: string | null;
  course_name?: string | null;
  start_date: string;
  end_date?: string | null;
  is_current_teaching: boolean;
}

export interface CourseItem {
  course_code: string;
  course_name: string;
  description?: string | null;
}
