from users.permissions import (IsStudentOrReadOnly,
                               IsSpecificStudent,
                               IsTeacherOrReadOnly,
                               IsSpecificTeacher,
                               IsAdminOrReadOnly)
from system_app.serializers import (StudentProfileSerializer,
                                    TeacherProfileSerializer,
                                    CourseSerializer,
                                    CourseStudentSerializer)
from system_app.models import StudentProfile, TeacherProfile, Course
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
class StudentProfileUpdate(generics.UpdateAPIView):
    queryset = StudentProfile.objects.all()
    permission_classes = [IsSpecificStudent]
    serializer_class = StudentProfileSerializer


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


class TeacherProfileUpdate(generics.UpdateAPIView):
    queryset = TeacherProfile.objects.all()
    permission_classes = [IsSpecificTeacher]
    serializer_class = TeacherProfileSerializer


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
    permission_classes = [IsStudentOrReadOnly, IsAuthenticated]

    def get_queryset(self):
        return [course for course in Course.objects.all() if course.available]


# Register for new courses.
class RegisterToCourse(generics.CreateAPIView):
    serializer_class = CourseStudentSerializer
    permission_classes = [IsStudentOrReadOnly, IsAuthenticated]

    def get_queryset(self):
        return [course for course in Course.objects.all() if course.available]
