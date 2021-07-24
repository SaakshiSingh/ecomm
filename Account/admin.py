from django.contrib import admin
from .models import *
from .forms import DiaryForm
# Register your models here.


@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
	       
	list_display = ('title','diary_user',"dateCreated","dateModified")
	search_fields = ('title',)
	list_display_links = ()
	filter_horizontal = ()
	list_filter = ()
	
admin.site.register(Customer)

@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
	       
	list_display = ('type_of_mood','mood_user','dateTime')	