from django.urls import path
from system_app.views import (StudentProfileCreate,
                              TeacherProfileCreate,
                              CourseCreate,
                              CourseList,
                              CourseListAvailable,
                              RegisterToCourse,
                              CourseParticipating,
                              StudentProfileDetail,
                              TeacherProfileDetail,
                              CourseTeaching)


urlpatterns = [
    path("student/create-profile/", StudentProfileCreate.as_view(), name="student-create"),
    path("student/<int:student_pk>/", StudentProfileDetail.as_view(), name="student-detail"),
    path("student/<int:student_pk>/course-available/", CourseListAvailable.as_view(), name="course-available"),
    path("student/<int:student_pk>/course-available/register/", RegisterToCourse.as_view(), name="register-to-course"),
    path("student/<int:student_pk>/course-participating/", CourseParticipating.as_view(), name="course-participating"),

    path("teacher/create-profile/", TeacherProfileCreate.as_view(), name="teacher-create"),
    path("teacher/<int:teacher_pk>/", TeacherProfileDetail.as_view(), name="teacher-detail"),
    path("teacher/<int:teacher_pk>/course-teaching/", CourseTeaching.as_view(), name="course-teaching"),

    path("admin/create-course/", CourseCreate.as_view(), name="course-create"),
    path("admin/course-list/", CourseList.as_view(), name="course-list"),

]
