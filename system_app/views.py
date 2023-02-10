import io
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from django.db.models import Sum
from rest_framework.decorators import action
import pandas as pd
from django.http import HttpResponse
from django.utils.encoding import smart_str
from users.permissions import (IsStudentOrReadOnly, IsTeacherOrReadOnly, IsAdminOrReadOnly)
from system_app.serializers import (StudentProfileSerializer,
                                    TeacherProfileSerializer,
                                    CourseSerializer,
                                    CourseSerializers,
                                    CreateAssignmentSerializer,
                                    StudentAssignmentSerializer,
                                    CourseAvailableSerializer,
                                    StudentAssignmentGradeSerializer,
                                    UpdateCourseSerializer,)
from system_app.models import (StudentProfile, TeacherProfile, Course, Assignment, StudentAssignment)
from collections import defaultdict


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

    @action(detail=True, methods=["GET"], serializer_class=CourseAvailableSerializer)
    def course_available(self, request, pk):
        if str(self.request.user.student_profile.id) != pk:
            raise ValidationError({"error": "Please correct your correct id student! (URL)"})
        courses = [course.id for course in Course.objects.all() if course.available]
        course = Course.objects.filter(id__in=courses)
        serializer = self.get_serializer(course, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"],)
    def course_participating(self, request, pk):
        if str(self.request.user.student_profile.id) != pk:
            raise ValidationError({"error": "You are not allowed for this action!"})
        student = defaultdict(list)
        course = StudentAssignment.objects.filter(student=pk).values("assignment__course__subject", "student_id", "grade")
        for c in course:
            student[c["assignment__course__subject"]].append(c["grade"])
        return Response(student)

    @action(detail=True, methods=["GET"])
    def average_progress(self, request, pk, course_pk):
        if self.request.user.student_profile.id != pk:
            raise ValidationError({"error": "You are not allowed for this action!"})
        if Course.objects.filter(student=pk, id=course_pk).exists():
            courses = Course.objects.filter(student=pk, id=course_pk)
            if StudentAssignment.objects.filter(student=pk, assignment__course=course_pk).exists():
                course = StudentAssignment.objects.filter(student=pk, assignment__course=course_pk)
                sum1 = course.aggregate(Sum("grade"))
                avg_grade = sum1["grade__sum"]/course.values("grade").count()
                course1 = StudentAssignment.objects.filter(student=pk, assignment__course=course_pk, content__isnull=False).count()
                progress = course1/3
                return Response({"course": course.values("assignment__course__subject")[0]["assignment__course__subject"],
                                 "avg_grade": avg_grade, "progress": progress})
            return Response({"course": courses.values("subject")[0]["subject"], "avg_grade": 0, "progress": 0})
        return Response({"error": "No results found!!"})

    @action(detail=True, methods=["GET"])
    def outstanding_assignments(self, request, pk, course_pk):
        if self.request.user.student_profile.id != pk:
            raise ValidationError({"error": "You are not allowed for this action!"})
        outstanding = Course.objects.filter(student=pk, id=course_pk, assignment_course__assignment_student__content__isnull=True)
        if outstanding.exists():
            return Response(outstanding.values("subject", "assignment_course__subject"))
        return Response({"Message": "You have no outstanding assignments for this course"})

    @action(detail=True, methods=["PUT"], serializer_class=[UpdateCourseSerializer])
    def register_to_course(self, request, pk, course_pk):
        if self.request.user.student_profile.id != pk:
            raise ValidationError({"error": "Please enter your correct ID!!"})
        courses = [course.id for course in Course.objects.all() if course.available]
        count = 0
        for i in courses:
            if Course.objects.filter(student=pk, id=i):
                count += 1
        if count == 3:
            raise ValidationError({"error": "You are already registered in 3 available courses!"})
        student = StudentProfile.objects.get(pk=pk)
        serializer = UpdateCourseSerializer(student, data=request.data)
        if serializer.is_valid():
            course = Course.objects.get(id=course_pk)
            if course_pk not in courses:
                course.wait_list.append(pk)
                course.save()
                raise ValidationError({"error": "You are added in wait-list! Please choose an available course!"})
            if Course.objects.filter(student=pk, id=course_pk).exists():
                raise ValidationError({"error": "You are already registered in this course!"})
            course.student.add(student)
            course.nr_students = course.nr_students + 1
            course.save()
            serializer.save(student=student)
            return Response({'Message': 'Registration was successful!!!!'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["GET"], serializer_class=CourseSerializers)
    def assignment_list(self, request, pk, course_pk):
        course = Course.objects.filter(student=pk, id=course_pk)
        serializer = CourseSerializers(course, many=True)
        return Response(serializer.data)

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

    @action(detail=True, methods=["GET"], serializer_class=CourseSerializers)
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
        courses = Course.objects.filter(teacher_id=pk, id=course_pk).values("student", "student__first_name")
        result = {}
        for student in courses:
            course1 = StudentAssignment.objects.filter(student=student["student"], assignment__course=course_pk,
                                                   content__isnull=False).count()
            progress = course1 / 3
            result[student["student"]] = {"student": student["student__first_name"], "progress": progress}
        return Response(result)

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

    @action(detail=True, methods=["GET"],)
    def student_assignments(self, request, pk, course_pk):
        assignments = StudentAssignment.objects.filter(assignment__course__teacher=pk, assignment__course=course_pk)
        return Response({"assignment": assignments.values()})

    @action(detail=True, methods=["PATCH"], serializer_class=[StudentAssignmentGradeSerializer])
    def grade_assignment(self, request, pk, course_pk, assignment_pk):
        assignment = StudentAssignment.objects.get(id=assignment_pk)
        serializer = StudentAssignmentGradeSerializer(assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)


class AdminViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # permission_classes = [IsAdminOrReadOnly]

    @action(detail=False, methods=["GET"])
    def new_students(self, request):
        filename = "new_students.xlsx"
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer) as writer:
            d = pd.read_csv("/home/shpresa/Desktop/school-system/new_students.csv")
            df = d.dropna(subset=["first_name"]).loc[d["country"] != "Russia"]
            df.to_excel(writer, index=False)

        response = HttpResponse(content=buffer.getvalue(), content_type="application/ms-excel")
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    @action(detail=False, methods=["GET"],)
    def students_average(self, request):
        filename = "students_average.xlsx"
        buffer = io.BytesIO()

        # list of all the students and grade point average
        df1 = pd.DataFrame(
            list(StudentProfile.objects.all().values("id", "first_name", "student_assignment__grade"))).groupby(
            by=["id", "first_name"]).apply(lambda x: x.sum() / x.count()).rename(
            columns={"student_assignment__grade": "avg_grade"})

        # all the students and their grade point average per course.
        df2 = pd.DataFrame(
            list(StudentProfile.objects.all().values("id", "first_name", "student_assignment__grade",
                                                     "student_assignment__assignment__course__subject"))).rename(
            columns={"student_assignment__grade": "grades", "student_assignment__assignment__course__subject": "Course"}).groupby(
            by=["id", "first_name", "Course"]).agg(list)
        df2["average"] = df2["grades"].apply(lambda x: sum(x)/3)
        table = pd.pivot_table(df2, values="average", index="first_name", columns="Course")

        with pd.ExcelWriter(buffer) as writer:
            df1.to_excel(writer, sheet_name="students_average")
            table.to_excel(writer, sheet_name="students_average_per_course")

        response = HttpResponse(content=buffer.getvalue(), content_type="application/ms-excel")
        response['Content-Disposition'] = f"attachment; filename={filename}"
        return response

    @action(detail=False, methods=["GET"])
    def student_data(self, request, pk):
        filename = "student_data.xlsx"
        buffer = io.BytesIO()

        # a student breakdown of the courses
        df1 = pd.DataFrame(list(StudentAssignment.objects.filter(student=pk).values("assignment__course__subject", "content"))).rename(
            columns={"assignment__course__subject": "subject", "content": "progress"}).groupby(
            "assignment__course__subject")[["content"]].apply(lambda x: x.count()/3)
        # df = pd.Series({"subject": "general progression", "progress": df1["progress"].sum()})
        # pd.concat([df1, df.to_frame().T], ignore_index=True)

        # a grade report per student
        df2 = pd.DataFrame(list(StudentAssignment.objects.filter(student=pk).values("assignment__course__subject", "grade"))).rename(
            columns={"assignment__course__subject": "subject"}).groupby(
            "subject").agg({"grade": lambda x: list(x)})

        with pd.ExcelWriter(buffer) as writer:
            df1.to_excel(writer, sheet_name="student_progress")
            df2.to_excel(writer, sheet_name="student_grade_report")

        response = HttpResponse(content=buffer.getvalue(), content_type="application/ms-excel")
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    @action(detail=False, methods=["GET"], )
    def top_students_courses(self, request):
        filename = "top_students_courses.xlsx"
        buffer = io.BytesIO()

        # top 10 students
        df1 = pd.DataFrame(
            list(StudentProfile.objects.all().values("id", "first_name", "student_assignment__grade"))).groupby(
            by=["id", "first_name"]).apply(lambda x: x.sum() / x.count()).rename(
            columns={"student_assignment__grade": "avg_grade"}).sort_values(by="avg_grade", ascending=False).iloc[:10]

        # the best performing courses
        df = pd.DataFrame(
            list(Course.objects.all().values("id", "subject", "assignment_course__assignment_student__grade"))).groupby(
            by=["id", "subject"]).apply(lambda x: (x.sum() / x.count())).rename(
            columns={"assignment_course__assignment_student__grade": "average"})
        df2 = df.loc[df["average"] > 5]

        with pd.ExcelWriter(buffer) as writer:
            df1.to_excel(writer, sheet_name="top_students")
            df2.to_excel(writer, sheet_name="best_performing_courses")

        response = HttpResponse(content=buffer.getvalue(), content_type="application/ms-excel")
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    # @action(detail=False, methods=["GET"], )
    # def best_performing_courses(self, request):
    #     df = pd.DataFrame(list(Course.objects.all().values("id", "subject", "assignment_course__assignment_student__grade"))).groupby(
    #         by=["id", "subject"]).apply(lambda x: (x.sum() / x.count())).rename(
    #         columns={"assignment_course__assignment_student__grade": "average"})
    #     dfg = df.loc[df["average"] > 5]
    #     dfg.to_excel("best_performing_courses.xlsx", sheet_name="best_performing_courses")
    #     with open("best_performing_courses.xlsx", "rb") as file:
    #         response = HttpResponse(file.read(), content_type="application/vnd.ms-excel")
    #         response['Content-Disposition'] = 'attachment; filename=%s' % smart_str("best_performing_courses.xlsx")
    #         return response

# from django.core import mail
# subject = "This course is available!"
# body = "We invite you to register in this course!"
# from1 = "shpresa@gmail.com"
# to = StudentProfile.objects.get(id=Course.objects.get(id=3).wait_list[0]).email
#
# with mail.get_connection() as connection:
#     mail.EmailMessage(
#         subject, body, from1, [to],
#         connection=connection,
#     ).send()


"""
The HTTP Content Disposition is a response-type header field that gives information 
on how to process the response payload and additional information such as filename 
when user saves it locally. This response header field holds a number of values and 
parameters in the larger context of MIME (Multipurpose Internet Mail Extensions). 
However, it reduces to a fixed set of parameters and values under HTTP forms and 
POST requests. 

@action is used to make methods in existing ViewSets routable:
If you have ad-hoc methods that should be routable, you can mark them as such with the @action decorator.
@api_view "converts" normal function based view functions to DRF views. 

Label vs. Location
The main distinction between the two methods is:
loc gets rows (and/or columns) with particular labels.
iloc gets rows (and/or columns) at integer locations.
"""
