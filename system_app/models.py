from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from users.models import CustomUser
import datetime
from django.utils.dateparse import parse_date


class TeacherProfile(models.Model):
    first_name = models.CharField(max_length=25, default=None)
    last_name = models.CharField(max_length=25, default=None)
    email = models.EmailField(unique=True, default=None)
    address = models.CharField(max_length=55, default=None)
    phone = models.CharField(max_length=12, default=None)
    user_teacher = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="teacher_profile")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Course(models.Model):
    subject = models.CharField(max_length=45)
    started = models.DateTimeField()
    nr_students = models.IntegerField(default=0, validators=[MaxValueValidator(10)])
    wait_list = ArrayField(models.IntegerField(default=0), default=list)
    teacher = models.ForeignKey(TeacherProfile, related_name="course", on_delete=models.PROTECT)
    nr_assignments = models.IntegerField(default=0, validators=[MaxValueValidator(3)])
    student = models.ManyToManyField(StudentProfile,
                                     related_name="courses",
                                     through="StudentsCourseRelation")

    def __str__(self):
        return f"{self.subject}"

    @property
    def available(self):
        # if the course has started
        duration = datetime.datetime.now().date() - self.started.date()
        if duration.days > 0:
            return False
        return True

    """
    Although using the @property decorator can help you access model methods as attributes, 
    you can't filter QuerySets by them, use them for ordering, or any other operation that 
    makes use of the database engine.
    """


class StudentsCourseRelation(models.Model):
    student_id = models.ForeignKey(StudentProfile, related_name="student", on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course, related_name="course", on_delete=models.CASCADE)

    class Meta:
        unique_together = (("student_id", "course_id"),)


class Assignment(models.Model):
    student = models.ManyToManyField(StudentProfile,
                                     related_name="assignment_student")
    course_id = models.ForeignKey(Course, related_name="assignment_course", on_delete=models.CASCADE)
    content = models.FileField(verbose_name="assignment_content")
    subject = models.CharField(max_length=45)

    def __str__(self):
        return f"{self.subject}"


class StudentAssignment(models.Model):
    assignment_id = models.ForeignKey(Assignment, related_name="assignment_student", on_delete=models.CASCADE)
    student_id = models.ForeignKey(StudentProfile, related_name="student_assignment", on_delete=models.CASCADE)
    grade = models.FloatField(default=0)

    class Meta:
        unique_together = (("assignment_id", "student_id"),)

