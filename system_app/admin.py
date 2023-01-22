from django.contrib import admin
from system_app.models import StudentProfile, TeacherProfile, Course, StudentsCourseRelation

admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
admin.site.register(Course)
admin.site.register(StudentsCourseRelation)
