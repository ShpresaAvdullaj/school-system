from users.permissions import (IsStudentOrReadOnly,
                               IsSpecificStudent,
                               IsTeacherOrReadOnly,
                               IsSpecificTeacher,
                               IsAdminOrReadOnly)
from system_app.serializers import (StudentProfileSerializer,
                                    TeacherProfileSerializer,
                                    CourseSerializer,
                                    CourseStudentSerializer,
                                    AssignmentSerializer)
from system_app.models import StudentProfile, TeacherProfile, Course, StudentsCourseRelation
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated


class StudentProfileCreate(generics.CreateAPIView):
    permission_classes = [IsStudentOrReadOnly]
    serializer_class = StudentProfileSerializer

    # will recognize the new student as a specific user
    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        # to be sure that the student will create only one, not an infinity students
        create_student_data_queryset = StudentProfile.objects.filter(user_student=self.request.user)
        if create_student_data_queryset.exists():
            raise ValidationError("You have already created your profile, but you can still update it.")

        serializer.save(user_student=self.request.user)


# Edit some personal data like: address, phone, email..
class StudentProfileDetail(generics.RetrieveUpdateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsSpecificStudent]

    def get_queryset(self):
        pk = self.kwargs["student_pk"]
        return StudentProfile.objects.filter(id=pk)


class CourseParticipating(generics.ListAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [IsSpecificStudent]

    def get_queryset(self):
        pk = self.kwargs["student_pk"]
        if self.request.user.student_profile.id == pk:
            return StudentsCourseRelation.objects.filter(student_id=pk)
        else:
            raise ValidationError({"error": "You are not allowed for this action!"})

class TeacherProfileCreate(generics.CreateAPIView):
    permission_classes = [IsTeacherOrReadOnly]
    serializer_class = TeacherProfileSerializer

    # will recognize the new teacher as a specific user
    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        # to be sure that the teacher will create only one, not an infinity teachers
        create_teacher_data_queryset = TeacherProfile.objects.filter(user_teacher=self.request.user)
        if create_teacher_data_queryset.exists():
            raise ValidationError("You have already created your profile, but you can still update it.")

        serializer.save(user_teacher=self.request.user)


class TeacherProfileDetail(generics.RetrieveUpdateAPIView):
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsSpecificTeacher]

    def get_queryset(self):
        pk = self.kwargs["teacher_pk"]
        return TeacherProfile.objects.filter(id=pk)


class CourseTeaching(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsSpecificTeacher]

    def get_queryset(self):
        pk = self.kwargs["teacher_pk"]
        if self.request.user.teacher_profile.id == pk:
            return Course.objects.filter(teacher_id=pk)
        else:
            raise ValidationError({"error": "You are not allowed for this action!"})


class CourseCreate(generics.CreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]


class CourseList(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]


# Student can see only courses available for the next semester.
class CourseListAvailable(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsSpecificStudent, IsAuthenticated]

    def get_queryset(self):
        pk = self.kwargs["student_pk"]
        if self.request.user.student_profile.id == pk:
            return [course for course in Course.objects.all() if course.available]
        raise ValidationError({"error": "Please correct your correct id student! (URL)"})


# Register for new courses.
class RegisterToCourse(generics.CreateAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [IsSpecificStudent, IsAuthenticated]

    # to allow a list with data, ListSerializer
    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(RegisterToCourse, self).get_serializer(*args, **kwargs)

    # to make sure that the id that the student enters is the same of student_id
    # that the request.user.student_profile has
    # to register in exactly three available courses
    # course capacity is 10 students
    def perform_create(self, serializer):
        pk = self.kwargs.get("student_pk")
        student = StudentProfile.objects.get(pk=pk)
        courses = [course.id for course in Course.objects.all() if course.available]
        count = 0
        for i in courses:
            if StudentsCourseRelation.objects.filter(student_id=self.request.user.student_profile, course_id=i):
                count += 1
        if count > 0:
            raise ValidationError({"error": "You are already registered in available courses!"})
        if len(serializer.validated_data) != 3:
            raise ValidationError({"error": "You must register in exactly 3 courses!"})
        for i in range(3):
            if serializer.validated_data[i]["student_id"].id != student.id or student.id != self.request.user.student_profile.id:
                raise ValidationError({"error": "Please enter your correct id!"})
            if serializer.validated_data[i]["course_id"].id not in courses:
                raise ValidationError({"error": "Please choose an available course!"})
            course = Course.objects.get(id=serializer.validated_data[i]["course_id"].id)
            if course.nr_students < 10:
                course.nr_students = course.nr_students + 1
            else:
                course.wait_list.append(serializer.validated_data[i]["student_id"].id)
            course.save()
        serializer.save()


# CREATE AN ASSIGNMENT
# class AssignmentCreate(generics.CreateAPIView):
#
# class AssignmentSubmit(generics.UpdateAPIView):
# two different serializers for the same model for different users
