from django.conf.urls import url
from django.contrib import admin

from class_app import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'index/task/', views.index_task),
    url(r'index/message/', views.index_message),
    url(r'index/', views.index),
    url(r'index_request/', views.index_request),
    url(r'index_p/',views.index_p),
    url(r'index_lt/', views.index_lt),
    url(r'index_submit/', views.index_submit),
    url(r'index_tj/', views.index_tj),
    url(r'check_code/', views.check_code),
    url(r'register/', views.register),
    url(r'logout/', views.logout),
    url(r'teacher/task/',views.teacher_task),
    url(r'teacher/submit/',views.teacher_submit),
    url(r'teacher/ajax/',views.teacher_ajax),
    url(r'teacher/', views.teacher),
    url(r'teacher_k/', views.teacher_k),
    url(r'teacher_k_bt/', views.teacher_k_bt),
    url(r'teacher_bt/remove/', views.teacher_bt_remove),
    url(r'teacher_nr/remove/', views.teacher_nr_remove),
    url(r'adviser_p/', views.adviser_p),
    url(r'adviser/', views.adviser),
    url(r'adviser_lt/', views.adviser_lt),
    url(r'adviser_tj/', views.adviser_tj),
    url(r'adviser_request/',views.adviser_request),


]