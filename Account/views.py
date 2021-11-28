from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from .models import *
from .filters import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .decorators import unauntheticated_user
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.core import serializers
from datetime import datetime, timedelta

import pandas as pd
from django.urls import reverse
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.conf import settings
from .utils import token_generator

import boto3
import random

from twilio.rest import Client
import razorpay

from django.views.decorators.csrf import csrf_exempt
@login_required(login_url='login')
@csrf_exempt
def success(request):
	if(request.method=="POST"):
		a=request.POST
		order_id = ""
		data = {}
		for key,val in a.items():
			if key == "razorpay_order_id":
				data['razorpay_order_id'] = val
			elif key == "razorpay_payment_id":
				data['razorpay_payment_id'] = val
			elif key == "razorpay_signature":
				data['razorpay_signature'] =val
				

		customer = Customer.objects.filter(payment_id =data['razorpay_order_id']).first()
		print(data)
		
		client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
		
		check = client.utility.verify_payment_signature(data)
		if check:
			return render(request,'Account/Error.html')

		customer.hasPremium = True
		customer.save()
	context={}
	return render(request,'Account/payment_Success.html')

@login_required(login_url='login')
def payment(request):
	client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
	order_amount = 50000
	order_currency = 'INR'
	payment = client.order.create(dict(amount=order_amount, currency=order_currency,payment_capture=1))
	payment_id = payment['id']
	customer = request.user.customer

	customer.payment_id = payment_id
	customer.save()
	
	context={'api_key':settings.RAZORPAY_API_KEY,'order_id':payment_id,'order_amount':order_amount}
	return render(request,'Account/payment.html',context)

	
def send_otp(mobile,otp):
	account_sid = settings.ACCOUNT_SID
	auth_token = settings.AUTH_TOKEN
	client = Client(account_sid,auth_token)
	message = client.messages.create(
		body='Otp for MooDiary is'+str(otp),
		from_ = settings.FROM_MOBILE,
		to=str(mobile)
	)

@unauntheticated_user
def home(request):
	context ={'title':"MooDiary"}
	return render(request,'Account/home.html',context)

def send_verification_mail(name,send_to_email,pk,domain,user):
	uidb64 = urlsafe_base64_encode(force_bytes(pk))
	link = reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})
	activate_url ='http://'+domain+link
	body = "Hello "+ name+ " You just registerd at our Digital Diary MooDiary. Please use the link to confirm Email for continuation.\n"+ activate_url
	email = EmailMessage(
		'Email Verification For MooDiary',
		body,
		settings.EMAIL_HOST_USER,
		[send_to_email],
		)
	email.send(fail_silently =False)

@unauntheticated_user
def registerPage(request):
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		
		if form.is_valid():
			check_useremail = User.objects.filter(email=request.POST.get('email')).first()
			if check_useremail:
				messages.error(request,'Account with this email already exists.')
				return redirect('login')

			check_userphone = Customer.objects.filter(phone=request.POST.get('phone')).first()
			if check_userphone:
				messages.error(request,'Account with this phone number already exists.')
				return redirect('login')

			user = form.save()
			name = user.username
			send_to_email = user.email
			pk = user.id
			domain = get_current_site(request).domain
			send_verification_mail(name,send_to_email,pk,domain,user)
			phone = form.cleaned_data.get('phone')
			user.customer.phone = phone
			otp = str(random.randint(100000,999999))
			user.customer.otp = otp
			user.save()
			send_otp(phone,otp)
			request.session['phone'] = str(phone)

			#messages.success(request,'Account successfully created')
			return redirect('otp')
	else:
		form = CreateUserForm()
		
	context ={'form':form}
	return render(request,'Account/register.html',context)

@unauntheticated_user
def otp(request):
	phone = request.session.get('phone')
	print(phone)
	if request.method =="POST":
		otp = request.POST.get("otp")
		obj = Customer.objects.filter(phone=phone).first()
		if(obj.otp == otp):
			print("YES")
			messages.success(request,'Account successfully created')
			obj.is_phone_verified=True
			obj.save()
			return redirect('login')
		else:
			print("NO")
			messages.error(request,'Invalid OTP')
	
	context ={'phone':phone}
	return render(request,'Account/otp.html',context)

@unauntheticated_user
def loginPage(request):
	
	if request.method =='POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request,username=username,password=password)
		if user is not None:
			if user.username =="user":
				login(request,user)
				return redirect('userpage')

			if not user.customer.is_email_verified:
				messages.error(request,'Your Email is not verified please check your mail')
			else:
				login(request,user)
				return redirect('userpage')
		else:
			messages.error(request,"UserName or password is incorrect")
			
	context ={}
	return render(request,'Account/login.html',context)

@login_required(login_url='login')
def logoutPage(request):
	logout(request)
	context ={}
	return render(request,'Account/home.html',context)



@login_required(login_url='login')
def user_page(request):

	diary = request.user.customer.diary_set.all()

	total_diary = diary.count()
	myFilter = DiaryFilter(request.GET,queryset=diary)
	diary = myFilter.qs

	context={'diary':diary,'total_diary':total_diary,'myFilter':myFilter,}
	return render(request,'Account/userpage.html',context)


def diary_chart(request):
	diary = request.user.customer.diary_set.all()
	diary.order_by('-dateCreated')
	firstPostDate =diary[0].dateCreated
	start="2021-07-01"
	date_list = pd.date_range(firstPostDate,datetime.today()).to_list()
	labels =[]
	for i in date_list:
		labels.append(i.date())
	
	data = []
	for i in date_list:
		data.append(diary.filter(dateCreated = i).count())
	

	return JsonResponse(data={
        'labels': labels,
        'data': data,
    },safe=False)

@login_required(login_url='login')
def create_diary(request):
	if request.method == 'POST':
		form = DiaryForm(request.POST,request.FILES)
		if form.is_valid():
			obj = form.save(commit=False)
			obj.writer = request.user.customer
			image_bytes = request.FILES['picture'].read()
			
			client = boto3.client('rekognition', region_name='ap-south-1')
			response = client.detect_faces(Image={'Bytes': image_bytes},Attributes=['ALL'])
			mood = max(response['FaceDetails'][0]['Emotions'],key=lambda x: x['Confidence'])['Type']
			obj.mood = mood
			obj.save()
			
			messages.success(request,'Diary Created')
			return redirect('userpage')
	else:
		form = DiaryForm()

	context={'form':form,'update':'false'}
	return render(request,'Account/createDiary.html',context)

@login_required(login_url='login')
def update_diary(request,pk):
	diary = Diary.objects.get(id=pk)
	form = DiaryForm(instance=diary)
	if request.method == 'POST':
		form = DiaryForm(request.POST,request.FILES,instance = diary)
		if form.is_valid():
			obj = form.save(commit=False)
			image_bytes = request.FILES['picture'].read()
			
			client = boto3.client('rekognition', region_name='ap-south-1')
			response = client.detect_faces(Image={'Bytes': image_bytes},Attributes=['ALL'])
			mood = max(response['FaceDetails'][0]['Emotions'],key=lambda x: x['Confidence'])['Type']
			obj.mood = mood
			obj.save()
			
			messages.success(request,'Diary Updated')
			return redirect('userpage')

	context={'form':form,'update':'true'}
	return render(request,'Account/createDiary.html',context)



@login_required(login_url ='login')
def delete_diary(request,pk):
	diary = Diary.objects.get(id=pk)
	if request.method == "POST":
		diary.delete()
		return redirect('userpage')
	context={'item':diary}
	return render(request,'Account/deleteDiary.html',context)


class VerificationView(View):
	def get(self,request,uidb64,token):
		try:
			uid = force_text(urlsafe_base64_decode(uidb64))
			print("uid is ",uid)
			user = User.objects.get(id=uid)
			print("name is ",user.username)
		except Exception as e:
			user = None 
		if user and token_generator.check_token(user,token):
			user.customer.is_email_verified =True
			user.customer.save()
		
		return redirect('login')
@login_required(login_url ='login')		
def watch_mood(request):
	moods = request.user.customer.mood_set.all()
	total = moods.count()
	print(moods)

	context={'moods':moods,'total':"hey",}
	return render(request,'Account/watchMood.html',context)


@login_required(login_url ='login')
def track_mood(request):
	if request.method == 'POST':
		form = MoodForm(request.POST)
		if form.is_valid():
			obj = form.save(commit=False)
			obj.writer = request.user.customer
			obj.save()
			messages.success(request,'Mood Recorded')
			return redirect('trackmood')
	else:
		form = MoodForm()

	search = False
	if request.method == 'GET':
		dateForm = DateInputForm(request.GET)
		if dateForm.is_valid():
			search = True
			date = dateForm.cleaned_data['date']
			request.session['date'] = str(date)
	
	
	
	context={'form':form,'dateForm':dateForm,'search':search}

	return render(request,'Account/trackMood.html',context)

def mood_chart(request):
	mood = request.user.customer.mood_set.all()
	#mymood = mood.order_by('dateTime')
	
	
	if(request.session['date']):
		sDate = request.session['date']
		oDate = datetime.strptime(sDate, '%Y-%m-%d')
		mood = mood.filter(dateTime__gte = oDate)
	
	new_date = datetime.today() - timedelta(days=7)
	date_list = pd.date_range(new_date,datetime.today()).to_list()



	date_labels =[]
	for i in date_list:
		date_labels.append(i.date())

	mood_list=[]
	heat_mood_list=[]
	for i in date_list:
		mood_list=[]
		for j in mood.filter(dateTime = i):
			for k in j.type_of_mood :
				mood_list.append(k)
		mood_set = set(mood_list)
		heat_mood_list.append(list(mood_set))



	list_mood =[]
	for i in mood:
		list_mood.append(i.type_of_mood)
	
	all_moods=[]
	for moods in list_mood:
		for mood in moods:
			all_moods.append(mood)
	mood_set = set(all_moods)
	
	mood_dict ={}
	for mood in mood_set:
		mood_dict[mood] = all_moods.count(mood)
	labels =[]
	data =[]
	for mood,value in mood_dict.items():
		labels.append(mood)
		data.append(value)

	

	list_of_all_moods =["happy", "sad", "anxious","calm","relaxed","angry","fearful","depressed","lonely","surprised","annoyed","nervous","sick","sleepy","excited","stressed","grumpy","scared","bored"]
	final_list=[]
	for moodData in list_of_all_moods:
		days =[]
		for day in heat_mood_list:
			if moodData in day:
				days.append(1)
			else:
				days.append(0)
		final_list.append(days)

	return JsonResponse(data={
        'labels':labels,
        'data':data,
        'final_list':final_list,
        'date_list':date_labels,
    },safe=False)



