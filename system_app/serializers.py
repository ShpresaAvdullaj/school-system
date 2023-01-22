from rest_framework import serializers
from system_app.models import (StudentProfile,
                               TeacherProfile,
                               Course,
                               StudentsCourseRelation)


class StudentProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentProfile
        # fields = "__all__"
        exclude = ("user_student",)


class TeacherProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherProfile
        # fields = "__all__"
        exclude = ("user_teacher",)


class CourseSerializer(serializers.ModelSerializer):
    available = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ("subject", "started", "teacher", "available",)
        # exclude = ("nr_assignments", "student",)


class CourseStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentsCourseRelation
        fields = "__all__"

    def save(self):

        course = self.validated_data["course_id"]
        if course in [course for course in Course.objects.all() if course.available]:
            serializer = StudentsCourseRelation(course_id=self.validated_data["course_id"],
                                                student_id=self.validated_data["student_id"])
            serializer.save()
            return serializer
        else:
            raise serializers.ValidationError("Please choose an available course")
