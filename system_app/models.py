from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from users.models import CustomUser
import datetime


class TeacherProfile(models.Model):
    first_name = models.CharField(max_length=25, default=None)
    last_name = models.CharField(max_length=25, default=None)
    email = models.EmailField(unique=True, default=None)
    address = models.CharField(max_length=55, default=None)
    phone = models.CharField(max_length=12, default=None)
    user_teacher = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="teacher_profile")

    # def __str__(self):
    #     return f"{self.first_name} {self.last_name}"


GENDER = (
    ("Female", "Female"),
    ("Male", "Male"),
    ("Poly-gender", "Poly-gender"),
    ("A-gender", "A-gender"),
    ("Non-binary", "Non-binary"),
    ("Gender-fluid", "Gender-fluid"),
    ("Gender-queer", "Gender-queer"),
    ("Bi-gender", "Bi-gender")
)


class StudentProfile(models.Model):
    first_name = models.CharField(max_length=25, default=None)
    last_name = models.CharField(max_length=25, default=None)
    email = models.EmailField(unique=True, default=None)
    address = models.CharField(max_length=55, default=None)
    gender = models.CharField(choices=GENDER, default=None, max_length=35)
    country = models.CharField(max_length=32, default=None)
    birth_date = models.DateTimeField(default=None)
    # the user with role student is created, so when a student logged in, he is already a user,
    # he can only create his data and update them
    user_student = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="student_profile")

    # def __str__(self):
    #     return f"{self.first_name} {self.last_name}"


class Course(models.Model):
    subject = models.CharField(max_length=45)
    started = models.DateTimeField()
    nr_students = models.IntegerField(default=0, validators=[MaxValueValidator(10)])
    wait_list = ArrayField(models.IntegerField(default=0), default=list)
    teacher = models.ForeignKey(TeacherProfile, related_name="course", on_delete=models.PROTECT)
    nr_assignments = models.IntegerField(default=0, validators=[MaxValueValidator(3)])
    student = models.ManyToManyField(StudentProfile, related_name="courses")

    # def __str__(self):
    #     return f"{self.subject}"

    @property
    def available(self):
        duration = self.started.date() - datetime.datetime.now().date()
        if 0 < duration.days <= 90 and self.nr_students < 10:
            return True
        return False

    """
    Although using the @property decorator can help you access model methods as attributes, 
    you can't filter QuerySets by them, use them for ordering, or any other operation that 
    makes use of the database engine.
    """


class Assignment(models.Model):
    student = models.ManyToManyField(StudentProfile,
                                     related_name="assignment_student")
    course = models.ForeignKey(Course, related_name="assignment_course", on_delete=models.CASCADE)
    subject = models.CharField(max_length=45)

    # def __str__(self):
    #     return f"{self.subject}"


class StudentAssignment(models.Model):
    assignment = models.ForeignKey(Assignment, related_name="assignment_student", on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, related_name="student_assignment", on_delete=models.CASCADE)
    content = models.CharField(verbose_name="assignment_content", default=None, max_length=100)
    grade = models.FloatField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("assignment", "student"),)

    @property
    def graded(self):
        if self.grade:
            return True
        return False

    @property # NOT CORRECT, or if duration/id modulo3 < 30
    def on_time(self):
        course = Course.objects.get(assignment_course__assignment_student=self.id)
        duration = self.created.date() - course.started.date()
        if duration.days > 30:
            return False
        return True
