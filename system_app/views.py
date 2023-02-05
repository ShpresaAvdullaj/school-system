from users.permissions import (IsStudentOrReadOnly,
                               IsTeacherOrReadOnly,
                               IsAdminOrReadOnly)
from system_app.serializers import (StudentProfileSerializer,
                                    TeacherProfileSerializer,
                                    CourseSerializer,
                                    CreateAssignmentSerializer,
                                    StudentAssignmentSerializer,
                                    StudentAssignmentGradeSerializer,
                                    UpdateCourseSerializer,)
from system_app.models import (StudentProfile,
                               TeacherProfile,
                               Course,
                               Assignment,
                               StudentAssignment)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from django.db.models import Sum
from rest_framework.decorators import action


class StudentProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStudentOrReadOnly]
    serializer_class = StudentProfileSerializer

    def get_queryset(self):
        pk = self.kwargs["pk"]
        if str(self.request.user.student_profile.id) != pk:
            raise ValidationError({"error": "You are not allowed for this action!"})
        return StudentProfile.objects.filter(id=pk)

    def perform_create(self, serializer):
        if StudentProfile.objects.filter(user_student=self.request.user).exists():
            raise ValidationError("You have already created your profile, but you can still update it.")
        serializer.save(user_student=self.request.user)

    @action(detail=True, methods=["GET"], serializer_class=[CourseSerializer])
    def course_available(self, request, pk):
        if str(self.request.user.student_profile.id) != pk:
            raise ValidationError({"error": "Please correct your correct id student! (URL)"})
        courses = [course.id for course in Course.objects.all() if course.available]
        queryset = Course.objects.filter(id__in=courses).values()
        return Response(queryset)

    @action(detail=True, methods=["GET"])
    def course_participating(self, request, pk):
        if str(self.request.user.student_profile.id) != pk:
            raise ValidationError({"error": "You are not allowed for this action!"})
        course = Course.objects.filter(student=pk)
        return Response(course.values("subject", "assignment_course__subject",
                                      "assignment_course__assignment_student__grade"))

    @action(detail=True, methods=["GET"])
    def average_progress(self, request, pk, course_pk):
        if self.request.user.student_profile.id != pk:
            raise ValidationError({"error": "You are not allowed for this action!"})
        if Course.objects.filter(student=pk, id=course_pk).exists():
            course = Course.objects.filter(student=pk, id=course_pk)
            sum1 = course.aggregate(Sum("assignment_course__assignment_student__grade"))
            avg_grade = sum1["assignment_course__assignment_student__grade__sum"]/course.values("assignment_course__assignment_student__grade").count()
            course1 = Course.objects.filter(student=pk, id=course_pk,
                                   assignment_course__assignment_student__content__isnull=False).count()
            progress = course1/3
            return Response({"course": course.values("subject"), "avg_grade": avg_grade, "progress": progress})
        return Response({"error": "No results found!!"})

    @action(detail=True, methods=["GET"])
    def outstanding_assignments(self, request, pk, course_pk):
        if self.request.user.student_profile.id != pk:
            raise ValidationError({"error": "You are not allowed for this action!"})
        outstanding = Course.objects.filter(student=pk, id=course_pk, assignment_course__assignment_student__content__isnull=True)
        if outstanding.exists():
            return Response(outstanding.values("subject", "assignment_course__subject"))

    @action(detail=True, methods=["PUT"], serializer_class=[UpdateCourseSerializer])
    def register_to_course(self, request, pk):
        if str(self.request.user.student_profile.id) != pk:
            raise ValidationError({"error": "Please enter your correct ID!!"})
        courses = [course.id for course in Course.objects.all() if course.available]
        count = 0
        for i in courses:
            if Course.objects.filter(student=pk, id=i):
                count += 1
        if count == 3:
            raise ValidationError({"error": "You are already registered in available courses!"})
        student = StudentProfile.objects.get(pk=pk)
        serializer = UpdateCourseSerializer(student, data=request.data)
        if serializer.is_valid():
            course = Course.objects.get(id=request.data.get('id'))
            if request.data.get('id') not in courses:
                course.wait_list.append(pk)
                raise ValidationError({"error": "Please choose an available course!"})
            course.student.add(student)
            course.nr_students = course.nr_students + 1
            course.save()
            serializer.save(student=student)
            return Response({'Message': 'Registration was successful!!!!'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"],)
    def assignment_list(self, request, pk, course_pk):
        return Response(Assignment.objects.filter(course_id=course_pk, course__student=pk).values("subject","assignment_student__content", "assignment_student__grade"))

    @action(detail=True, methods=["POST"], serializer_class=[StudentAssignmentSerializer])
    def submit_assignment(self, request, pk, course_pk, assignment_pk):
        serializer = StudentAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student_id=pk, assignment_id=assignment_pk)
            return Response(serializer.data)


class TeacherProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTeacherOrReadOnly]
    serializer_class = TeacherProfileSerializer

    def get_queryset(self):
        pk = self.kwargs["pk"]
        if str(self.request.user.teacher_profile.id) != pk:
            raise ValidationError({"error": "You are not allowed for this action!"})
        return TeacherProfile.objects.filter(id=pk)

    def perform_create(self, serializer):
        if TeacherProfile.objects.filter(user_teacher=self.request.user).exists():
            raise ValidationError("You have already created your profile, but you can still update it.")
        serializer.save(user_teacher=self.request.user)

    @action(detail=True, methods=["GET"], serializer_class=CourseSerializer)
    def course_teaching(self, request, pk):
        if pk != str(self.request.user.teacher_profile.id):
            raise ValidationError({"error": "You are not allowed for this action!"})
        courses = Course.objects.filter(teacher_id=pk)
        if courses.exists():
            serializer = self.get_serializer(courses, many=True)
            return Response(serializer.data)

    @action(detail=True, methods=["GET"],)
    def students_signed(self, request, pk, course_pk):
        if pk != self.request.user.teacher_profile.id:
            raise ValidationError({"error": "You are not allowed for this action!"})
        courses = Course.objects.filter(teacher_id=pk, id=course_pk)
        return Response(courses.values("subject", "student__first_name"))

    @action(detail=True, methods=["POST"], serializer_class=[CreateAssignmentSerializer])
    def create_assignment(self, request, pk, course_pk):
        course = Course.objects.get(id=course_pk, teacher_id=pk)
        serializer = CreateAssignmentSerializer(data=request.data)
        if course.nr_assignments == 3:
            raise ValidationError({"error": "You can not create more than 3 assignments for each course!!"})
        if serializer.is_valid():
            course.nr_assignments = course.nr_assignments + 1
            course.save()
            serializer.save(course=course)
            return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def student_assignments(self, request, pk, course_pk):
        assignments = StudentAssignment.objects.filter(assignment__course__teacher=pk, assignment__course=course_pk)
        return Response(assignments.values())

    @action(detail=True, methods=["PATCH"], serializer_class=[StudentAssignmentGradeSerializer])
    def grade_assignment(self, request, pk, course_pk, assignment_pk):
        assignment = StudentAssignment.objects.get(id=assignment_pk)
        serializer = StudentAssignmentGradeSerializer(assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]

# class AssignmentGrade(generics.UpdateAPIView):
#     serializer_class = StudentAssignmentGradeSerializer
#     permission_classes = [IsTeacherOrReadOnly]
#
#     def get_queryset(self):
#         pk = self.kwargs.get("pk")
#         return StudentAssignment.objects.filter(pk=pk)
#
#     def perform_update(self, serializer):
#         pk = self.kwargs.get("pk")
#         assignment = StudentAssignment.objects.get(pk=pk)
#         assignment1 = StudentsCourseRelation.objects.get(course_id__assignment_course__assignment_student=assignment.id, student_id__student_assignment=assignment.id)
#         assignment1.grades.append(serializer.validated_data["grade"])
#         assignment1.avg_grade = (sum(assignment1.grades) + serializer.validated_data["grade"])/3
#         assignment1.save()
#         serializer.save()


# class CourseParticipatingRegisterViewSet(viewsets.ModelViewSet):
#     serializer_class = CourseStudentSerializer
    # permission_classes = [IsStudentOrReadOnly, IsAuthenticated]
    #
    # # Register for new courses.
    # # to allow a list with data, ListSerializer
    # # bulk_create does not work with many-to-many relationships
    # def get_serializer(self, *args, **kwargs):
    #     if isinstance(kwargs.get("data", {}), list):
    #         kwargs["many"] = True
    #
    #     return super(CourseParticipatingRegisterViewSet, self).get_serializer(*args, **kwargs)

    # to make sure that the id that the student enters is the same of student_id
    # that the request.user.student_profile has
    # to register in exactly three available courses
    # course capacity is 10 students
    # def perform_create(self, serializer):
    #     pk = self.kwargs.get("student_pk")
    #     student = StudentProfile.objects.get(pk=pk)
    #     if self.request.user.student_profile.id != pk:
    #         raise ValidationError({"error": "Please enter your correct ID!!"})
    #     courses = [course.id for course in Course.objects.all() if course.available]
    #     count = 0
        # for i in courses:
        #     if StudentsCourseRelation.objects.filter(student_id=student, course_id=i):
        #         count += 1
        # if count > 0:
        #     raise ValidationError({"error": "You are already registered in available courses!"})
        # if len(serializer.validated_data) != 3:
        #     raise ValidationError({"error": "You must register in exactly 3 courses!"})
        # for i in range(3):
        #     if serializer.validated_data[i]["course_id"].id not in courses:
        #         raise ValidationError({"error": "Please choose an available course!"})
        #     course = Course.objects.get(id=serializer.validated_data[i]["course_id"].id)
        #     if course.nr_students < 10:
        #         course.nr_students = course.nr_students + 1
        #     else:
        #         course.wait_list.append(pk)
        #     course.save()
        # serializer.save(student_id=student)


# class AssignmentViewSet(viewsets.ModelViewSet):
#     serializer_class = AssignmentSerializer
#     permission_classes = [IsTeacherOrReadOnly, IsAuthenticated]

    # LIST OF ASSIGNMENTS PER COURSES THAT HE TEACHING
    # def get_queryset(self):
    #     pk = self.kwargs.get("course_pk")
    #     pk1 = self.kwargs.get("teacher_pk")
    #     assignment = Assignment.objects.filter(course_id=pk, course__teacher=pk1)
    #     return assignment

    # CREATE ASSIGNMENTS FOR COURSES THAT HE TEACHING

    # def perform_create(self, serializer):
    #     pk = self.kwargs.get("course_pk")
    #     pk1 = self.kwargs.get("teacher_pk")
    #     course = Course.objects.get(pk=pk, teacher_id=pk1)
    #     if course.nr_assignments >= 3:
    #         raise ValidationError({"error": "You can not create more than 3 assignments for each course!!"})
    #     course.nr_assignments = course.nr_assignments + 1
    #     course.save()
    #     serializer.save(course_id=course.id)
    #

# # LIST OF ASSIGNMENTS PER COURSES THAT HE PARTICIPATES
# class AssignmentStudentParticipate(generics.ListAPIView):
#     permission_classes = [IsStudentOrReadOnly]
#     serializer_class = AssignmentSerializer
#
#     def get_queryset(self):
#         pk = self.kwargs.get("course_pk")
#         pk1 = self.kwargs.get("student_pk")
#         assignment = Assignment.objects.filter(course_id=pk, course__student=pk1)
#         return assignment

from django.core.exceptions import ObjectDoesNotExist

# OUTSTANDING ASSIGNMENT
# class OutstandingAssignments(generics.ListAPIView):
#     # permission_classes = [IsStudentOrReadOnly]
#     serializer_class = AssignmentSerializer
#
#     def get_queryset(self):
#         pk = self.kwargs.get("course_pk")
#         pk1 = self.kwargs.get("student_pk")
#         for assign in Assignment.objects.filter(course_id=pk, course__student=pk1):
#             try:
#                 StudentAssignment.objects.filter(assignment_id=assign.id, student_id=pk1)
#                 return assign
#             except ObjectDoesNotExist:
#                 return assign



# SUBMIT AN ASSIGNMENT
# class AssignmentSubmit(generics.CreateAPIView):
#     permission_classes = [IsStudentOrReadOnly]
    # serializer_class = StudentAssignmentSerializer
    #
    # def perform_create(self, serializer):
    #     pk = self.kwargs.get("student_pk")
    #     pk1 = self.kwargs.get("assignment_pk")
    #     serializer.save(student_id=pk, assignment_id=pk1)


# GRADE AN ASSIGNMENT
# class AssignmentGrade(generics.UpdateAPIView):
    # serializer_class = StudentAssignmentGradeSerializer
    # permission_classes = [IsTeacherOrReadOnly]
    #
    # def get_queryset(self):
    #     pk = self.kwargs.get("pk")
    #     return StudentAssignment.objects.filter(pk=pk)
    #
    # def perform_update(self, serializer):
    #     pk = self.kwargs.get("pk")
    #     assignment = StudentAssignment.objects.get(pk=pk)
    #     assignment1 = StudentsCourseRelation.objects.get(course_id__assignment_course__assignment_student=assignment.id, student_id__student_assignment=assignment.id)
    #     assignment1.grades.append(serializer.validated_data["grade"])
    #     assignment1.avg_grade = (sum(assignment1.grades) + serializer.validated_data["grade"])/3
    #     assignment1.save()
    #     serializer.save()

# will recognize the new student as a specific user
# def get_object(self):
#     return self.request.user

"""@action is used to make methods in existing ViewSets routable:
If you have ad-hoc methods that should be routable, you can mark them as such with the @action decorator.
@api_view "converts" normal function based view functions to DRF views. """


# from system_app.models import (StudentProfile,
#                                StudentsCourseRelation)
# import pandas as pd
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from users.permissions import IsAdminOrReadOnly
#
# # - view list of all the students and grade point average.
# class ListStudents(APIView):
#     # permission_classes = [IsAdminOrReadOnly]
#
#     def get(self, request, format=None):
#         df = pd.DataFrame(list(StudentsCourseRelation.objects.all().values("student_id", "avg_grade"))).groupby("student_id").mean()
#         return Response(df.to_json())
#
# # Generate a grade report per student.
# # If you click on a student you can see the breakdown of the courses
# class GradeReportPerStudent(APIView):
#     # permission_classes = [IsAdminOrReadOnly]
#
#     def get(self, request, pk, format=None):
#         df = pd.DataFrame(list(StudentsCourseRelation.objects.filter(student_id_id=pk).values("student_id", "course_id", "grades", "avg_grade"))).groupby("student_id", group_keys=True).apply(lambda x: x)
#         df["progress"] = df["grades"].str.len() / 3
#         # print(df["progress"].sum()) general progression
#         return Response(df.to_json())
#
#
# #  View top 10 students in the school
# class BestStudents(APIView):
#     # permission_classes = [IsAdminOrReadOnly]
#
#     def get(self, request, format=None):
#         df = pd.DataFrame(list(StudentsCourseRelation.objects.all()
#                                .values("student_id", "avg_grade"))).groupby("student_id").mean().sort_values(
#             by="avg_grade", ascending=False).iloc[:10]
#         return Response(df.to_json())
#
# """
# Label vs. Location
# The main distinction between the two methods is:
# loc gets rows (and/or columns) with particular labels.
# iloc gets rows (and/or columns) at integer locations.
# """
#
#
# # -View the best performing courses with average grade above 80 %
# class BestPerformingCourses(APIView):
#     # permission_classes = [IsAdminOrReadOnly]
#
#     def get(self, request, format=None):
#         df = pd.DataFrame(list(StudentsCourseRelation.objects.all().values("course_id", "avg_grade"))).groupby(
#             "course_id").mean()
#         d = df.apply(lambda row: row[df["avg_grade"] > 5])
#         return Response(d.to_json())
#
#
# #  View all the students grouped by - country
# class GroupByGender(APIView):
#     # permission_classes = [IsAdminOrReadOnly]
#
#     def get(self, request, format=None):
#         df = pd.DataFrame(list(StudentProfile.objects.all().values())).groupby("gender", group_keys=True).apply(lambda x: x)
#         return Response(df.to_json())
#
#
# #  View all the students grouped by - country
# class GroupByCountry(APIView):
#     # permission_classes = [IsAdminOrReadOnly]
#
#     def get(self, request, format=None):
#         df = pd.DataFrame(list(StudentProfile.objects.all().values())).groupby("country", group_keys=True).apply(lambda x: x)
#         return Response(df.to_json())
#
#
# # -Generate a report that contains all the students and their grade point average per course.
# class StudentAveragePerCourse(APIView):
#     # permission_classes = [IsAdminOrReadOnly]
#
#     def get(self, request, format=None):
#         df = pd.DataFrame(list(StudentsCourseRelation.objects.all().values("student_id","course_id","avg_grade"))).groupby("student_id", group_keys=True).apply(lambda x: x)
#         return Response(df.to_json())
#
#
# # Admin needs to import a list of incoming students for the new year.
# # - Filter out all the students where the name is blank
# # - Filter out students from Russia since there is an embargo.
# class ListNewStudents(APIView):
#     # permission_classes = [IsAdminOrReadOnly]
#
#     def get(self, request, format=None):
#         df = pd.read_csv("/home/shpresa/Desktop/school-system/new_students.csv")
#         dfg = df.dropna(subset=["first_name"]).loc[df["country"] != "Russia"]
#         return Response(dfg.to_json(indent=2, orient='records', lines=True))
#
#
