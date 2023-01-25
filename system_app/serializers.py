from rest_framework import serializers
from system_app.models import (StudentProfile,
                               TeacherProfile,
                               Course,
                               StudentsCourseRelation,
                               Assignment)


class StudentProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentProfile
        exclude = ("user_student",)


class TeacherProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherProfile
        exclude = ("user_teacher",)


class CourseSerializer(serializers.ModelSerializer):
    available = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ("id", "subject", "started", "teacher", "available",)


class CourseStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentsCourseRelation
        fields = ("student_id", "course_id", )


class AssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment


class AssignmentSerializerStudent(serializers.ModelSerializer):

    class Meta:
        model = Assignment
