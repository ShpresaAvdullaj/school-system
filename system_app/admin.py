from django.contrib import admin
from system_app.models import (StudentProfile,
                               TeacherProfile,
                               Course,
                               # StudentsCourseRelation,
                               Assignment,
                               StudentAssignment)

admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
admin.site.register(Course)
# admin.site.register(StudentsCourseRelation)
admin.site.register(Assignment)
admin.site.register(StudentAssignment)
