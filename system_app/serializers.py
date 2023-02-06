from rest_framework import serializers
from system_app.models import (StudentProfile,
                               TeacherProfile,
                               Course,
                               Assignment,
                               StudentAssignment)


class StudentProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentProfile
        exclude = ("user_student",)


class TeacherProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherProfile
        exclude = ("user_teacher",)


class StudentAssignmentSerializer(serializers.ModelSerializer):
    graded = serializers.ReadOnlyField()
    on_time = serializers.ReadOnlyField()

    class Meta:
        model = StudentAssignment
        fields = ("content", "graded", "grade", "student_id", "assignment_id", "on_time")


class StudentAssignmentGradeSerializer(serializers.ModelSerializer):
    graded = serializers.ReadOnlyField()
    assignment_student = StudentAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = StudentAssignment
        fields = ("grade", "assignment_id", "graded", "assignment_student", )


class CreateAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        exclude = ("student", "course")


class CourseSerializer(serializers.ModelSerializer):
    available = serializers.ReadOnlyField()
    student = StudentProfileSerializer(many=True, read_only=True)
    assignment_course = CreateAssignmentSerializer(many=True, read_only=True)
    teacher = serializers.CharField(source="teacher.first_name", read_only=True)

    class Meta:
        model = Course
        fields = ("id", "subject", "started", "teacher", "available", "student", "assignment_course", )


class UpdateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ("started", "teacher", "subject", "student")


# class CourseAssignmentStudent(serializers.ModelSerializer):
#     available = serializers.ReadOnlyField()
#     teacher = serializers.CharField(source="teacher.first_name")
#     assignment_course = StudentAssignmentGradeSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Course
#         fields = ("id", "subject", "started", "teacher", "available", "assignment_course")
#

