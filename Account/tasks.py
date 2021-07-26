from Diary.celery import app
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task

@app.task(name='Account.tasks.send_notification')
def send_notification():
	from django.contrib.auth.models import User
	try:
		print("Hello")
		objs = User.objects.all()
		for obj in objs:
			if obj.customer.is_email_verified == True:
				subject = 'Reminder to WriteDiary'
				message = "This is your daily reminder to write a Digital journal"
				email = EmailMessage(
					subject,
					message,
					settings.EMAIL_HOST_USER,
					[obj.email],
					)
				print("Email sent to ",obj.username)
				email.send(fail_silently =False)
	except Exception as e:
		print(e)

