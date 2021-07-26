import django_filters
from . models import Diary,Mood
from django_filters import DateFilter
from django import forms


class DateInput(forms.DateInput):
	input_type = 'date'

class DiaryFilter(django_filters.FilterSet):
	title= django_filters.CharFilter(lookup_expr='icontains',widget=forms.TextInput(attrs={'id':'searchTitle','class':'form-control ','placeholder':'Title Search'}))
	content= django_filters.CharFilter(lookup_expr='icontains',widget=forms.TextInput(attrs={'id':'searchContent','class':'form-control ','placeholder':'Content Search'}))
	mood= django_filters.CharFilter(lookup_expr='icontains',widget=forms.TextInput(attrs={'id':'searchMood','class':'form-control ','placeholder':'Mood Search'}))
	date = DateFilter(field_name = 'dateCreated',lookup_expr='gte',widget=forms.TextInput(attrs={'id':'searchDate','class':'form-control datetimepicker-input','placeholder':'Diaries After the Date:','data-target':'#datetimepicker1'}))
	class Meta:	
		model = Diary
		exclude =['title','mood','content','dateCreated','picture','writer','dateModified']
