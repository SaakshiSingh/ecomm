from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomerPasswordResetForm,CustomerSetPasswordForm

urlpatterns = [

    path('',views.home,name = "home"),
    path('register/',views.registerPage,name="register"),
    path('login/',views.loginPage,name="login"),
    path('logout/',views.logoutPage,name="logout"),
    path('userpage/',views.user_page,name="userpage"),
    path('creatediary/',views.create_diary,name = "creatediary"),
    path('updatediary/str<pk>',views.update_diary,name="updatediary"),
    path('deletediary/str<pk>',views.delete_diary,name="deletediary"),
    path('diarychart/', views.diary_chart, name='diary-chart'),
    path('moodchart/', views.mood_chart, name='mood-chart'),
    path('trackmood/',views.track_mood,name="trackmood"),
    path('activate/<uidb64>/<token>',views.VerificationView.as_view(),name="activate"),
    path('reset_password/',
        auth_views.PasswordResetView.as_view(template_name = "Account/registration/password_reset.html",
        form_class=CustomerPasswordResetForm,email_template_name='Account/registration/password_reset_email.html',
        subject_template_name = 'Account/registration/password_reset_subject.txt',),

        name ="password_reset" ),
    path('reset_password_sent/',
        auth_views.PasswordResetDoneView.as_view(template_name = "Account/registration/password_reset_done.html"),
        name ="password_reset_done"),
    path('reset/<uidb64>/<token>',
        auth_views.PasswordResetConfirmView.as_view(form_class=CustomerSetPasswordForm,template_name = "Account/registration/password_reset_confirm.html"),
        name ="password_reset_confirm"),
    path('reset_password_complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name = "Account/registration/password_reset_complete.html"),
        name ="password_reset_complete"),
]
