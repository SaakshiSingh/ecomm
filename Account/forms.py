from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm,PasswordResetForm,SetPasswordForm
from django.contrib.auth.models import User
from django import forms
from .models import *
from ckeditor.widgets import CKEditorWidget

from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.contrib.auth import password_validation
from django.contrib.admin.widgets import AdminDateWidget,AdminTimeWidget

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget


class CustomerSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomerSetPasswordForm, self).__init__(*args, **kwargs)
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'id':'floatingPassReset1','placeholder': 'New Password', 'class': 'form-control'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'id':'floatingPassReset1','placeholder': 'Repeat Password', 'class': 'form-control'}),
    )
 
class CustomerPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CustomerPasswordResetForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Email',
        'type': 'email',
        'name': 'email',
        'id':'floatingEmail_reset'
        }))



class CreateUserForm(UserCreationForm):
	
	username = forms.CharField(widget = forms.TextInput(attrs={
		'id':'floatingUsername','class':'form-control ','placeholder':'UserName'}))
	email = forms.CharField(widget=forms.EmailInput(attrs={
		'id':'floatingEmail','class': 'form-control ','placeholder':'Email'}))
	phone = PhoneNumberField(widget=forms.TextInput(attrs={
		'id':'floatingPhone','class': 'form-control ','placeholder':'Mobile Number'}))
	
	password1 = forms.CharField(widget=forms.PasswordInput(attrs={
		'id':'floatingPass1','class': 'form-control ','placeholder':'Password1'}))
	password2 = forms.CharField(widget=forms.PasswordInput(attrs={
		'id':'floatingPass2','class': 'form-control ','placeholder':'Password2'}))

	class Meta:
		model = User
		fields = ['username','email','phone','password1','password2']




class DiaryForm(ModelForm):
	class Meta:
		model = Diary
		exclude =['writer']

	title = forms.CharField(widget = forms.TextInput(attrs={
		'id':'diaryTitle','class':'form-control form-title',}))
	#content = forms.CharField(widget=forms.Textarea(attrs={'id':'diaryContent','class':'form-control colorValue','rows':'10','cols':'80',}))
	content = forms.CharField(widget=CKEditorWidget(attrs={
		'rows':'10'}))
	picture = forms.ImageField(widget = forms.FileInput(attrs={
		'id':'picture','class':'form-control form-control-sm'}))

class DateInput(forms.DateInput):
	input_type = 'date'
	
class MoodForm(ModelForm):
	class Meta:
		model = Mood
		include = '__all__'
		exclude =['writer','dateTime']

	

	

class DateInputForm(forms.Form):
	date = forms.DateField(widget = DateInput)