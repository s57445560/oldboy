from django.db import models

# Create your models here.


class User_type(models.Model):  # 用户角色表
    user_type = models.CharField(max_length=32)

    def __str__(self):
        return self.user_type


class Campus(models.Model):     # 校区表
    name = models.CharField(max_length=32,blank=True,null=True)

    def __str__(self):
        return self.name


class UserInfo(models.Model):       # 用户信息标
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    source = models.CharField(max_length=32,blank=True,null=True)
    change_time = models.DateTimeField(auto_now=True)
    make_time = models.DateTimeField(auto_now_add=True)
    campus = models.ForeignKey('Campus')
    user_type_id = models.ForeignKey('User_type')



class Course(models.Model):         # 课程表
    name = models.CharField(max_length=32)
    change_time = models.DateTimeField(auto_now=True)
    make_time = models.DateTimeField(auto_now_add=True)
    b = models.ManyToManyField('UserInfo')
    campus = models.ForeignKey('Campus')


class Course_content(models.Model):     # 课程内容表
    name = models.CharField(max_length=32)
    change_time = models.DateTimeField(auto_now=True)
    make_time = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey('Course')


class Task(models.Model):               # 作业情况表
    username = models.CharField(max_length=32)
    task_content = models.CharField(max_length=64)
    change_time = models.DateTimeField(auto_now=True)
    make_time = models.DateTimeField(auto_now_add=True)
    mark = models.CharField(max_length=32,blank=True,null=True)
    course_content_id = models.ForeignKey('Course_content')


class Sign_up(models.Model):            # 报名确认表
    course_name = models.CharField(max_length=32)
    user_name = models.CharField(max_length=32)
    school_id = models.CharField(max_length=32,blank=True,null=True)


class Chat_p(models.Model):               # 咨询内容记录
    user_name = models.CharField(max_length=32)
    course_name = models.CharField(max_length=32, blank=True, null=True)
    adviser_name = models.CharField(max_length=32)
    status = models.CharField(max_length=32)
    message = models.CharField(max_length=64)
    school_id = models.CharField(max_length=32, blank=True, null=True)
    make_time = models.DateTimeField(auto_now_add=True,blank=True, null=True)
