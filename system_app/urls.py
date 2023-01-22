from django.urls import path
from system_app.views import (StudentProfileCreate,
                              StudentProfileUpdate,
                              TeacherProfileCreate,
                              TeacherProfileUpdate,
                              CourseCreate,
                              CourseList,
                              CourseListAvailable,
                              RegisterToCourse)


urlpatterns = [
    path("student/create-profile/", StudentProfileCreate.as_view(), name="student-create"),
    path("student/<int:pk>/edit/", StudentProfileUpdate.as_view(), name="student-detail"),
    path("student/<int:pk>/course-available/", CourseListAvailable.as_view(), name="course-available"),
    path("student/course-available/<int:pk>/", RegisterToCourse.as_view(), name="register-to-course"),

    path("teacher/create-profile/", TeacherProfileCreate.as_view(), name="teacher-create"),
    path("profile/teacher/<int:pk>/edit/", TeacherProfileUpdate.as_view(), name="teacher-detail"),

    path("admin/create-course/", CourseCreate.as_view(), name="course-create"),
    path("admin/course-list/", CourseList.as_view(), name="course-list"),

]
