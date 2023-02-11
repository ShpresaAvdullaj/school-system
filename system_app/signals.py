from django.dispatch import receiver
from django.db.models.signals import post_save
from system_app.models import Course
from django.core.mail import send_mail
from django.conf import settings

# from django.conf import settings
# from django.core.mail import send_mail
#
#
# def sending_mail(request):
#     send_mail(
#     subject='Add an eye-catching subject',
#     message='Write an amazing message',
#     from_email=settings.EMAIL_HOST_USER,
#     recipient_list=['shpresa.avdullaj@fshnstudent.info'],)

# to = StudentProfile.objects.get(id=Course.objects.get(id=3).wait_list[0]).email


#
# @receiver(post_save, sender=Course)
# def sending_mail(sender, instance=Course()):
#     if instance.started != instance.started and instance.available==True:
#         send_email()
