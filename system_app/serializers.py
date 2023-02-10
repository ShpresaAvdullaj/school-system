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


class CourseAvailableSerializer(serializers.ModelSerializer):
    available = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ("subject", "available", "started")


class UpdateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ("started", "teacher", "subject", "student")


class CreateAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        exclude = ("student", "course")


class CourseSerializer(serializers.ModelSerializer):
    available = serializers.ReadOnlyField()
    student = StudentProfileSerializer(many=True, read_only=True)
    assignment_course = CreateAssignmentSerializer(many=True, read_only=True)
    # teacher = serializers.CharField(source="teacher.first_name", read_only=True)

    class Meta:
        model = Course
        fields = ("id", "subject", "started", "teacher", "available", "student", "assignment_course", )


class CourseSerializers(serializers.ModelSerializer):
    available = serializers.ReadOnlyField()
    assignment_course = CreateAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ("subject", "started", "available", "assignment_course", )


class StudentAssignmentSerializer(serializers.ModelSerializer):
    on_time = serializers.ReadOnlyField()

    class Meta:
        model = StudentAssignment
        fields = ("content", "grade", "student_id", "assignment_id", "on_time")


class TeacherProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherProfile
        exclude = ("user_teacher",)


class StudentAssignmentGradeSerializer(serializers.ModelSerializer):
    assignment_student = StudentAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = StudentAssignment
        fields = ("grade", "assignment_id", "assignment_student", )

