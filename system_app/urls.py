from django.urls import path, include
from rest_framework.routers import DefaultRouter
from system_app.views import (StudentProfileViewSet,
                              TeacherProfileViewSet,
                              CourseViewSet,)

router = DefaultRouter()
router.register("teacher", TeacherProfileViewSet, basename="teacherportal")

router1 = DefaultRouter()
router1.register("student", StudentProfileViewSet, basename="studentportal")

urlpatterns = [
    path("", include(router1.urls)),
    path("course_available/", include(router1.urls)),
    path("course_participating/", include(router1.urls)),
    path("register_to_course/", include(router1.urls)),
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


    # path("teacher/<int:teacher_pk>/course-teaching/<int:course_pk>/assignment-list/", assignment_list, name="assignment-course-list"),
    # path("teacher/<int:teacher_pk>/course-teaching/<int:course_pk>/assignments/<int:pk>/", AssignmentGrade.as_view(),name="students-assignment-course-list"),



    path("admin/create-course/", CourseViewSet.as_view({"post": "create"}), name="course-create"),
    path("admin/course-list/", CourseViewSet.as_view({"get": "list"}), name="course-list"),
    path("admin/course-list/<int:pk>/", CourseViewSet.as_view({"get": "list"}), name="course-list"),

]
# assignment_list = AssignmentViewSet.as_view({"get": "list"})
# register_to_course = CourseParticipatingRegisterViewSet.as_view({"post": "create"})
# course_participating = CourseParticipatingRegisterViewSet.as_view({"get": "list"})
# path("student/create-profile/", StudentProfileViewSet.as_view({"post": "create"}), name="student-create"),
# path("student/<int:student_pk>/", StudentProfileViewSet.as_view({"get": "list"}), name="student-detail"),
# path("student/<int:student_pk>/course-available/", CourseListAvailable.as_view(), name="course-available"),
# path("student/<int:student_pk>/course-available/register/", register_to_course, name="register-to-course"),
# path("student/<int:student_pk>/course-participating/", course_participating, name="course-participating"),
# path("student/<int:student_pk>/course-participating/<int:course_pk>/assignment-list/", AssignmentStudentParticipate.as_view(), name="student-assignment-list"),
# path("student/<int:student_pk>/course-participating/<int:course_pk>/outstanding-assignments/",OutstandingAssignments.as_view(), name="outstanding-assignments"),
# path("student/<int:student_pk>/course-participating/<int:course_pk>/assignment-list/<int:assignment_pk>/submit/", AssignmentSubmit.as_view(), name="assignment-submit"),


# path("teacher/create-profile/", TeacherProfileViewSet.as_view({"post": "create"}), name="teacher-create"),
# path("teacher/<int:teacher_pk>/", TeacherProfileViewSet.as_view({"get": "list"}), name="teacher-detail"),
# path("teacher/<int:teacher_pk>/course-teaching/", TeacherProfileViewSet.as_view({"get": "list"}), name="course_teaching"),
# path("create-profile/", include(router.urls)),

# CourseParticipatingRegisterViewSet,
# AssignmentViewSet,
# AssignmentStudentParticipate,
# AssignmentSubmit,
# AssignmentGrade,)
# OutstandingAssignments)



# urlpatterns = [
#     path("students_average/", ListStudents.as_view(), name="list-students" ),
#     path("report_per_student/<int:pk>/", GradeReportPerStudent.as_view(), name="report-per-student" ),
#     path("best_students/", BestStudents.as_view(), name="best_students"),
#     path("best_performing_courses/", BestPerformingCourses.as_view(), name="best-performing-courses"),
#     path("group_by_country/", GroupByCountry.as_view(), name="group_by_country"),
#     path("group_by_gender/", GroupByGender.as_view(), name="group_by_gender"),
#     path("student_average_per_course/", StudentAveragePerCourse.as_view(), name="student_average_per_course"),
#     path("new_students/", ListNewStudents.as_view(), name="new-students"),
#
# ]


