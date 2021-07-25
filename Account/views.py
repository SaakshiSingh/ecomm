from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm,DiaryForm,MoodForm,DateInputForm
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


@unauntheticated_user
def home(request):
	context ={'title':"MooDiary"}
	return render(request,'Account/home.html',context)

@unauntheticated_user
def registerPage(request):
	
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			name = user.username
			send_to_email = user.email
			uidb64 = urlsafe_base64_encode(force_bytes(user.id))
		
			domain = get_current_site(request).domain

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
		
			messages.success(request,'Account successfully created')
			return redirect('login')
	else:
		form = CreateUserForm()
	context ={'form':form}
	return render(request,'Account/register.html',context)
	

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
			
			form.save()
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

	if request.method == 'GET':
		dateForm = DateInputForm(request.GET)
		if dateForm.is_valid():
			date = dateForm.cleaned_data['date']
			request.session['date'] = str(date)
	
	
	
	context={'form':form,'dateForm':dateForm}

	return render(request,'Account/trackMood.html',context)

def mood_chart(request):
	mood = request.user.customer.mood_set.all()
	mymood = mood.order_by('dateTime')
	firstMoodDate =mymood[0].dateTime
	
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
		for j in mymood.filter(dateTime = i):
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



