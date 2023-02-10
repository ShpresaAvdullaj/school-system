from django.urls import path, include
from rest_framework.routers import DefaultRouter
from system_app.views import (StudentProfileViewSet,
                              TeacherProfileViewSet,
                              AdminViewSet,)

router = DefaultRouter()
router.register("teacher", TeacherProfileViewSet, basename="teacherportal")

router1 = DefaultRouter()
router1.register("student", StudentProfileViewSet, basename="studentportal")

urlpatterns = [
    path("", include(router1.urls)),
    path("course_available/", include(router1.urls)),
    path("course_participating/", include(router1.urls)),
    path("student/<int:pk>/course_available/<int:course_pk>/register_to_course/",
         StudentProfileViewSet.as_view({"put": "register_to_course"}), name="register-to-course"),
    path("student/<int:pk>/course_participating/<int:course_pk>/assignment_list/",
         StudentProfileViewSet.as_view({"get": "assignment_list"}), name="student-assignment-list"),
    path("student/<int:pk>/course_participating/<int:course_pk>/assignment_list/<int:assignment_pk>/submit/",
         StudentProfileViewSet.as_view({"post": "submit_assignment"}), name="assignment-submit"),
    path("student/<int:pk>/course_participating/<int:course_pk>/",
         StudentProfileViewSet.as_view({"get": "average_progress"}), name="average-progress-per-course"),
    path("student/<int:pk>/course_participating/<int:course_pk>/outstanding/",
         StudentProfileViewSet.as_view({"get": "outstanding_assignments"}), name="outstanding-assignments"),



    path("", include(router.urls)),
    path("course_teaching/", include(router.urls)),
    path("teacher/<int:pk>/course_teaching/<int:course_pk>/create_assignment/",
         TeacherProfileViewSet.as_view({"post": "create_assignment"}), name="assignment-create"),
    path("teacher/<int:pk>/course_teaching/<int:course_pk>/student_assignment_list/",
         TeacherProfileViewSet.as_view({"get": "student_assignments"}), name="assignment-course-list"),
    path("teacher/<int:pk>/course_teaching/<int:course_pk>/student_assignment_list/<int:assignment_pk>/grade/",
         TeacherProfileViewSet.as_view({"patch": "grade_assignment"}), name="grade-assignment"),
    path("teacher/<int:pk>/course_teaching/<int:course_pk>/students_signed/",
         TeacherProfileViewSet.as_view({"get": "students_signed"}), name="students-signed"),


    path("admin/create-course/", AdminViewSet.as_view({"post": "create"}), name="course-create"),
    path("admin/course-list/", AdminViewSet.as_view({"get": "list"}), name="course-list"),
    path("admin/course-list/<int:pk>/", AdminViewSet.as_view({"get": "list"}), name="course-list"),
    path("admin/new_students/", AdminViewSet.as_view({"get": "new_students"}), name="new-students"),
    path("admin/students_average/", AdminViewSet.as_view({"get": "students_average"}), name="students_average"),
    path("admin/student/<int:pk>/student_data/", AdminViewSet.as_view({"get": "student_data"}), name="student_data"),
    path("admin/top_students_courses/", AdminViewSet.as_view({"get": "top_students_courses"}), name="top_students"),

]

# path("admin/student/<int:pk>/student_progress/", AdminViewSet.as_view({"get": "student_progress"}), name="student_progress"),
# path("admin/student/<int:pk>/grade_report_student/", AdminViewSet.as_view({"get": "grade_report_student"}), name="grade_report_student"),
# path("admin/best_performing_courses/", AdminViewSet.as_view({"get": "best_performing_courses"}), name="best_performing_courses"),
# path("admin/students_average_per_course/", AdminViewSet.as_view({"get": "students_average_per_course"}), name="students_average_per_course"),
