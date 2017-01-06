from django.shortcuts import render,HttpResponse, redirect
import json
# Create your views here.
from django import forms
from class_app import models

test_choices = (
    (0, '广告'),
    (1, '介绍'),
    (2, '51cto'),
    (3, '视频'),
)
class LoginForm(forms.Form):
    username = forms.CharField(required=True,min_length=5,max_length=20,
                               error_messages={'min_length':'账号长度不能小于5','max_length':'账号长度不能超过20','required':'账号不能为空'})
    pwd = forms.CharField(required=True, min_length=5, max_length=20,
                          error_messages={'min_length': '密码长度不能小于5', 'max_length': '密码长度不能超过20', 'required': '密码不能为空'})


class registerFrom(forms.Form):
    r_username = forms.CharField(required=True,min_length=5,max_length=20,
                                 error_messages={'min_length':'账号长度不能小于5','max_length':'账号长度不能超过20','required':'账号不能为空'})
    r_pwd = forms.CharField(required=True, min_length=5, max_length=20,
                            error_messages={'min_length': '密码长度不能小于5', 'max_length': '密码长度不能超过20', 'required': '密码不能为空'})
    rr_pwd = forms.CharField(required=True, min_length=5, max_length=20,
                             error_messages={'min_length': '密码长度不能小于5', 'max_length': '密码长度不能超过20',
                                            'required': '密码不能为空'})
    text_campus = models.Campus.objects.all().values_list('id', 'name')
    r_campus = forms.CharField(widget=forms.Select(choices=text_campus))
    r_source = forms.CharField(widget=forms.Select(choices=test_choices))

    def __init__(self, *args, **kwargs):
        super(registerFrom, self).__init__(*args, **kwargs)
        self.fields['r_campus'].widget.choices = models.Campus.objects.all().values_list('id', 'name')


class CourseFrom(forms.Form):
    coursename = forms.CharField(required=True,error_messages={'required': '账号不能为空'})


def auth(func):								# 登陆装饰器
    def inner(request, *args, **kwargs):
        user = request.session.get('user', None)			# 判断session内是否有user这个值
        if not user:
            return redirect('/')			# 如果没有就返回登陆页
        return func(request, *args, **kwargs)
    return inner



def home(request):
    result = {'status': False, 'message': None}
    obj = registerFrom()
    if request.session.get('user',None):
        if request.session['type'] == 2:        # 学员页面
            return redirect('/index/')
        elif request.session['type'] == 1:      # 老师页面
            return redirect('/teacher/')
        elif request.session['type'] == 3:      # 顾问页面
            return redirect('/adviser/')

    if request.method == 'POST':
        obj = LoginForm(request.POST)
        if obj.is_valid():
            print(obj.clean())
            code = request.POST.get('check_code')
            if code.upper() == request.session['CheckCode'].upper():
                username = request.POST.get('username')
                pwd = request.POST.get('pwd')
                user_obj = models.UserInfo.objects.filter(username=username,password=pwd).values('user_type_id', 'campus__name', 'campus__id', 'id')
                # print(user_obj,user_obj[0].user_type_id_id,'aaaaaaaaaaaaa')
                if user_obj:
                    result['status'] = True
                    request.session['user'] = username
                    request.session['type'] = user_obj[0]['user_type_id']
                    request.session['user_id'] = user_obj[0]['id']
                    request.session['school'] = user_obj[0]['campus__name']
                    request.session['school_id'] = user_obj[0]['campus__id']
                    request.session['user_select'] = False
                    print(user_obj,request.session['school'])
                else:
                    result['message'] = {'message': [{'message': "用户名或密码错误"}]}
            else:
                result['status'] = False
                result['message'] = {'message':[{'message': "验证码错误"}]}
        else:
            print(obj.errors.as_json())
            result['message'] = json.loads(obj.errors.as_json())
        return HttpResponse(json.dumps(result))
    return render(request, 'home.html',{'obj':obj})


# 专门处理图片的url
def check_code(request):
    import io
    from backend import check_code as CheckCode

    stream = io.BytesIO()
    # img图片对象,code在图像中写的内容
    img, code = CheckCode.create_validate_code()
    img.save(stream, "png")

    request.session["CheckCode"] = code
    return HttpResponse(stream.getvalue())


# 处理注册的url
def register(request):
    result = {'status': False, 'message': None}
    if request.POST:
        obj = registerFrom(request.POST)
        if obj.is_valid():
            print(obj.clean())
            r_username = request.POST.get('r_username',None)
            r_pwd = request.POST.get('r_pwd')
            rr_pwd = request.POST.get('rr_pwd')
            r_source = request.POST.get('r_source')
            r_campus = request.POST.get('r_campus')
            source = test_choices[int(r_source)]
            if r_pwd != rr_pwd:
                result['message'] = {'rr_pwd': [{'message': "密码与上次输入不一致"}]}
            else:
                user_obj = models.UserInfo.objects.filter(username=r_username)
                if user_obj:
                    result['message'] = {'r_username': [{'message': "用户已存在"}]}
                else:
                    models.UserInfo.objects.create(username=r_username, password=r_pwd, source=source[1],user_type_id_id=2,campus_id=r_campus)
                    user_obj = models.UserInfo.objects.filter(username=r_username, password=r_pwd).values('user_type_id',
                                                                                                      'campus__name',
                                                                                                      'campus__id',
                                                                                                      'id')
                    request.session['user'] = r_username
                    request.session['type'] = 2
                    request.session['user_id'] = user_obj[0]['id']
                    request.session['school'] = user_obj[0]['campus__name']
                    request.session['school_id'] = user_obj[0]['campus__id']
                    request.session['user_select'] = False
                    result['status'] = True

        else:
            print(obj.errors.as_json())
            result['message'] = json.loads(obj.errors.as_json())
        return HttpResponse(json.dumps(result))
    return redirect('/')



from django.utils.safestring import mark_safe
@auth
def index(request):
    if request.session['type'] == 2:
        xq = request.session['school_id']
        kc_all = models.Course.objects.filter(campus_id=xq).count()
        current_page = request.GET.get('p', 1)  # 获取GET请求的p数值 如过没有就设置为1
        # 每页显示10条数据
        # 第一页：0-10
        page_display_num = 3                    # 每页显示多少行
        current_page = int(current_page)
        start = (current_page - 1) * page_display_num  # 计算出从数据库里取数据的开始下标
        end = current_page * page_display_num  # 计算出从数据库里取数据的结束下标
        # 将所有的页码显示在页面上
        total_item = models.Course.objects.filter(campus_id=xq).all().count()
        all_page, remainder = divmod(total_item, page_display_num)  # 计算分页的总页数 如过b不等于0那么all_page就要加1
        if remainder != 0:
            all_page = all_page + 1
        begin = 0
        end_num = 0
        if all_page > 6:                        # 计算分页在web上显示的页数 分页显示5个
            all_num = all_page - 2
            if current_page > all_num:
                begin = all_num - 3
                end_num = all_num + 2
            elif current_page <= 2:
                begin = 0
                end_num = 5
            else:
                begin = current_page - 3
                end_num = current_page + 2
        else:
            begin = 0
            end_num = all_page
        list_page = []
        begin_page = "<a href='/index?p=1'>首页<a>"
        list_page.append(begin_page)
        if current_page == 1:
            prev = "<a href='#'>上一页<a>"
        else:
            prev = "<a href='/index?p=%s'>上一页<a>" % (current_page - 1)
        list_page.append(prev)
        for i in range(begin + 1, end_num + 1):
            if i == current_page:  # 当用户点击的是标签返回的就是那个GET请求p的数字 就选中这个标签
                temp = "<a class='active' href='/index?p=%s' > %s<a>" % (i, i)
            else:
                temp = "<a href='/index?p=%s'> %s<a>" % (i, i)
            list_page.append(temp)

        if current_page == all_page:
            down = "<a href='#'>下一页<a>"
        else:
            down = "<a href='/index?p=%s'>下一页<a>" % (current_page + 1)
        list_page.append(down)
        end_page = "<a href='/index?p=%s'>末页<a>" % all_page
        list_page.append(end_page)
        temp = ''.join(list_page)
        type_list = models.Course.objects.filter(campus_id=xq).all()[start:end]
        sun = models.UserInfo.objects.get(id=request.session.get('user_id'))
        t = sun.course_set.all()
        t_list = []
        for t_index in t:
            t_list.append(t_index.name)
        print(t_list)
        Sing_list = []
        Sign_obj = models.Sign_up.objects.filter(user_name=request.session['user']).values('course_name')
        for S_i in Sign_obj:
            Sing_list.append(''.join(list(S_i.values())))
        print(Sing_list)
        return render(request, 'index_home.html', {'type_list': type_list, 'str_page': mark_safe(temp), 'all_page': all_page,'kc_all':kc_all,'t_list':t_list,'Sing_list':Sing_list})
    else:
        return redirect('/')


@auth
def teacher(request):
    if request.session['type'] == 1:
        course_list = []
        print('111111111112222')
        xq = request.session['school_id']
        kc_all = models.Course.objects.filter(campus_id=xq).count()
        task_all = models.Course_content.objects.filter(course__campus__id=xq).count()
        user_all = models.UserInfo.objects.filter(campus_id=xq).count()

        return render(request,'teacher_home.html',{'kc_all':kc_all,'task_all':task_all,'user_all':user_all})
    else:
        return redirect('/')

@auth
def teacher_ajax(request):
    if request.session['type'] == 1:
        course_list = []
        result = {'status':True,'data':''}
        if request.POST:
            a = request.POST.get('user_select',None)
            xq = request.session['school_id']
            print(a)
            course_all = models.Course.objects.filter(campus_id=xq).all()
            for index in course_all:
                g1 = models.Course.objects.get(campus_id=xq, name=index.name)
                num = g1.b.count()
                course_list.append([str(index.name), num])
                print(index.name, num)
            print(course_list)
            result['data'] = course_list
            return HttpResponse(json.dumps(result))
    else:
        return redirect('/')

@auth
def adviser(request):
    if request.session['type'] == 3:
        xq = request.session['school_id']
        kc_all = models.Sign_up.objects.filter(school_id=xq).count()
        current_page = request.GET.get('p', 1)  # 获取GET请求的p数值 如过没有就设置为1
        # 每页显示10条数据
        # 第一页：0-10
        page_display_num = 3                    # 每页显示多少行
        current_page = int(current_page)
        start = (current_page - 1) * page_display_num  # 计算出从数据库里取数据的开始下标
        end = current_page * page_display_num  # 计算出从数据库里取数据的结束下标
        # 将所有的页码显示在页面上
        total_item = models.Sign_up.objects.filter(school_id=xq).all().count()
        all_page, remainder = divmod(total_item, page_display_num)  # 计算分页的总页数 如过b不等于0那么all_page就要加1
        if remainder != 0:
            all_page = all_page + 1
        begin = 0
        end_num = 0
        if all_page > 6:                        # 计算分页在web上显示的页数 分页显示5个
            all_num = all_page - 2
            if current_page > all_num:
                begin = all_num - 3
                end_num = all_num + 2
            elif current_page <= 2:
                begin = 0
                end_num = 5
            else:
                begin = current_page - 3
                end_num = current_page + 2
        else:
            begin = 0
            end_num = all_page
        list_page = []
        begin_page = "<a href='/adviser?p=1'>首页<a>"
        list_page.append(begin_page)
        if current_page == 1:
            prev = "<a href='#'>上一页<a>"
        else:
            prev = "<a href='/adviser?p=%s'>上一页<a>" % (current_page - 1)
        list_page.append(prev)
        for i in range(begin + 1, end_num + 1):
            if i == current_page:  # 当用户点击的是标签返回的就是那个GET请求p的数字 就选中这个标签
                temp = "<a class='active' href='/adviser?p=%s' > %s<a>" % (i, i)
            else:
                temp = "<a href='/adviser?p=%s'> %s<a>" % (i, i)
            list_page.append(temp)

        if current_page == all_page:
            down = "<a href='#'>下一页<a>"
        else:
            down = "<a href='/adviser?p=%s'>下一页<a>" % (current_page + 1)
        list_page.append(down)
        end_page = "<a href='/adviser?p=%s'>末页<a>" % all_page
        list_page.append(end_page)
        temp = ''.join(list_page)
        type_list = models.Sign_up.objects.filter(school_id=xq).all()[start:end]
        sun = models.UserInfo.objects.get(id=request.session.get('user_id'))
        t = sun.course_set.all()
        return render(request, 'adviser_home.html', {'type_list': type_list, 'str_page': mark_safe(temp), 'all_page': all_page,'kc_all':kc_all,'t':t})
    else:
        return redirect('/')


@auth
def adviser_p(request):
    if request.session['type'] == 3:
        xq = request.session['school_id']
        kc_all = models.UserInfo.objects.filter(campus_id=xq,user_type_id_id=2).count()
        current_page = request.GET.get('p1', 1)  # 获取GET请求的p数值 如过没有就设置为1
        # 每页显示10条数据
        # 第一页：0-10
        page_display_num = 3                    # 每页显示多少行
        current_page = int(current_page)
        start = (current_page - 1) * page_display_num  # 计算出从数据库里取数据的开始下标
        end = current_page * page_display_num  # 计算出从数据库里取数据的结束下标
        # 将所有的页码显示在页面上
        total_item = models.UserInfo.objects.filter(campus_id=xq,user_type_id_id=2).all().count()
        all_page, remainder = divmod(total_item, page_display_num)  # 计算分页的总页数 如过b不等于0那么all_page就要加1
        if remainder != 0:
            all_page = all_page + 1
        begin = 0
        end_num = 0
        if all_page > 6:                        # 计算分页在web上显示的页数 分页显示5个
            all_num = all_page - 2
            if current_page > all_num:
                begin = all_num - 3
                end_num = all_num + 2
            elif current_page <= 2:
                begin = 0
                end_num = 5
            else:
                begin = current_page - 3
                end_num = current_page + 2
        else:
            begin = 0
            end_num = all_page
        list_page = []
        begin_page = "<a href='/adviser_p?p1=1'>首页<a>"
        list_page.append(begin_page)
        if current_page == 1:
            prev = "<a href='#'>上一页<a>"
        else:
            prev = "<a href='/adviser_p?p1=%s'>上一页<a>" % (current_page - 1)
        list_page.append(prev)
        for i in range(begin + 1, end_num + 1):
            if i == current_page:  # 当用户点击的是标签返回的就是那个GET请求p的数字 就选中这个标签
                temp = "<a class='active' href='/adviser_p?p1=%s' > %s<a>" % (i, i)
            else:
                temp = "<a href='/adviser_p?p1=%s'> %s<a>" % (i, i)
            list_page.append(temp)

        if current_page == all_page:
            down = "<a href='#'>下一页<a>"
        else:
            down = "<a href='/adviser_p?p1=%s'>下一页<a>" % (current_page + 1)
        list_page.append(down)
        end_page = "<a href='/adviser_p?p1=%s'>末页<a>" % all_page
        list_page.append(end_page)
        temp = ''.join(list_page)
        type_list = models.UserInfo.objects.filter(campus_id=xq,user_type_id_id=2).all()[start:end]
        chat_list = []
        for user_name in type_list:
            chat_obj = models.Chat_p.objects.filter(user_name=user_name.username,school_id=request.session['school_id']).last()
            if chat_obj:
                if chat_obj.status == '1':
                    chat_list.append(chat_obj.user_name)

        return render(request, 'adviser_p.html', {'type_list': type_list, 'str_page': mark_safe(temp), 'all_page': all_page,'kc_all':kc_all,'chat_list':chat_list})
    else:
        return redirect('/')


@auth
def index_p(request):
    if request.session['type'] == 2:
        xq = request.session['school_id']
        kc_all = models.UserInfo.objects.filter(campus_id=xq,user_type_id_id=3).count()
        current_page = request.GET.get('p1', 1)  # 获取GET请求的p数值 如过没有就设置为1
        # 每页显示10条数据
        # 第一页：0-10
        page_display_num = 3                    # 每页显示多少行
        current_page = int(current_page)
        start = (current_page - 1) * page_display_num  # 计算出从数据库里取数据的开始下标
        end = current_page * page_display_num  # 计算出从数据库里取数据的结束下标
        # 将所有的页码显示在页面上
        total_item = models.UserInfo.objects.filter(campus_id=xq,user_type_id_id=3).all().count()
        all_page, remainder = divmod(total_item, page_display_num)  # 计算分页的总页数 如过b不等于0那么all_page就要加1
        if remainder != 0:
            all_page = all_page + 1
        begin = 0
        end_num = 0
        if all_page > 6:                        # 计算分页在web上显示的页数 分页显示5个
            all_num = all_page - 2
            if current_page > all_num:
                begin = all_num - 3
                end_num = all_num + 2
            elif current_page <= 2:
                begin = 0
                end_num = 5
            else:
                begin = current_page - 3
                end_num = current_page + 2
        else:
            begin = 0
            end_num = all_page
        list_page = []
        begin_page = "<a href='/index_p?p1=1'>首页<a>"
        list_page.append(begin_page)
        if current_page == 1:
            prev = "<a href='#'>上一页<a>"
        else:
            prev = "<a href='/index_p?p1=%s'>上一页<a>" % (current_page - 1)
        list_page.append(prev)
        for i in range(begin + 1, end_num + 1):
            if i == current_page:  # 当用户点击的是标签返回的就是那个GET请求p的数字 就选中这个标签
                temp = "<a class='active' href='/index_p?p1=%s' > %s<a>" % (i, i)
            else:
                temp = "<a href='/index_p?p1=%s'> %s<a>" % (i, i)
            list_page.append(temp)

        if current_page == all_page:
            down = "<a href='#'>下一页<a>"
        else:
            down = "<a href='/index_p?p1=%s'>下一页<a>" % (current_page + 1)
        list_page.append(down)
        end_page = "<a href='/index_p?p1=%s'>末页<a>" % all_page
        list_page.append(end_page)
        temp = ''.join(list_page)
        type_list = models.UserInfo.objects.filter(campus_id=xq,user_type_id_id=3).all()[start:end]
        chat_list = []
        for user_name in type_list:
            chat_obj = models.Chat_p.objects.filter(adviser_name=user_name.username,school_id=request.session['school_id'],user_name=request.session['user']).last()
            if chat_obj:
                if chat_obj.status == '2':
                    chat_list.append(chat_obj.adviser_name)

        return render(request, 'index_p.html', {'type_list': type_list, 'str_page': mark_safe(temp), 'all_page': all_page,'kc_all':kc_all,'chat_list':chat_list})
    else:
        return redirect('/')




def logout(request):
    del request.session['user']
    return redirect('/')


@auth
def teacher_k(request):
    if request.session['type'] == 1:
        content_data = ''
        result = {'status':False,'message':''}
        xq = request.session['school_id']
        if request.POST:
            name = request.POST.get('coursename',None)
            taskename = request.POST.get('taskename', None)
            if name:
                obj = models.Course.objects.filter(name=name, campus_id=xq).all()
                if not obj:
                    models.Course.objects.create(name=name,campus_id=xq)
                    result['status'] = True
                    return HttpResponse(json.dumps(result))
                else:
                    print('课程存在')
                    result['message'] = '课程存在'
                    return HttpResponse(json.dumps(result))
            elif taskename:
                print('111111')
                obj = models.Course_content.objects.filter(name=taskename).all()
                if not obj:
                    bt_id = request.session.get('bt_id', None)
                    if not bt_id:
                        result['message'] = '请先选择左侧创建的课程'
                        return HttpResponse(json.dumps(result))
                    models.Course_content.objects.create(name=taskename,course_id=bt_id)
                    result['status'] = True
                    return HttpResponse(json.dumps(result))
                else:
                    print('内容存在')
                    result['message'] = '内容存在'
                    return HttpResponse(json.dumps(result))
        else:
            bt_id = request.session.get('bt_id',None)
            if bt_id:
                content_data = models.Course_content.objects.filter(course__campus__id=xq,course_id=bt_id).all()
        data = models.Course.objects.filter(campus_id=xq).all()
        return render(request, 'teacher_kc.html', {'data':data,'content_data':content_data})
    else:
        return redirect('/')


@auth
def teacher_k_bt(request):
    if request.session['type'] == 1:
        if request.POST:
            id = request.POST.get('id',None)
            request.session['bt_id'] = id
        return HttpResponse('ok')
    else:
        return redirect('/')


@auth
def teacher_bt_remove(request):
    if request.session['type'] == 1:
        result = {'status': False, 'message': ''}
        print('aaaa')
        if request.POST:
            id = request.POST.get('id',None)
            g1 = models.Course.objects.get(id=id)
            if g1.b.all():
                result['message'] = '已有学生成功报名不能删除课程'
                return HttpResponse(json.dumps(result))
            if id:
                models.Course_content.objects.filter(course_id=id).delete()
                models.Course.objects.filter(id=id).delete()
                result['status'] = True
        return HttpResponse(json.dumps(result))
    else:
        return redirect('/')

@auth
def teacher_nr_remove(request):
    if request.session['type'] == 1:
        result = {'status': False, 'message': ''}
        if request.POST:
            id = request.POST.get('id',None)
            if id != 'false':
                models.Course_content.objects.filter(id=id).delete()
                result['status'] = True
            else:
                result['message'] = '请先选中删除的内容'
        return HttpResponse(json.dumps(result))
    else:
        return redirect('/')


@auth
def index_request(request):
    result = {'status': False, 'message': ''}
    if request.session['type'] == 2:
        if request.POST:
            bm = request.POST.get('bm')
            user = request.session['user']
            user_obj = models.UserInfo.objects.filter(username=user).all()
            kc_obj = models.Course.objects.filter(name=bm,campus_id=request.session['school_id']).all()
            g1 = models.Course.objects.get(id=int(kc_obj[0].id))
            cc_obj = g1.b.filter(username=user).all()
            if not cc_obj:
                models.Course.objects.get(id=kc_obj[0].id)
                obj = models.Sign_up.objects.filter(course_name=bm,user_name=request.session['user'],school_id=request.session['school_id']).all()
                if not obj:
                    models.Sign_up.objects.create(course_name=bm,user_name=request.session['user'],school_id=request.session['school_id'])
                    result['status'] = True
        return HttpResponse(json.dumps(result))
    else:
        return redirect('/')

@auth
def adviser_request(request):
    result = {'status': False, 'message': ''}
    if request.session['type'] == 3:
        if request.POST:
            bm = request.POST.get('bm')
            kc = request.POST.get('kc')
            bm_obj = models.UserInfo.objects.filter(username=bm).all()
            kc_obj = models.Course.objects.filter(name=kc,campus_id=request.session['school_id']).all()
            print(bm_obj[0].id,kc_obj[0].id)
            g1 = models.Course.objects.get(id=kc_obj[0].id)
            g1.b.add(bm_obj[0])
            models.Sign_up.objects.filter(user_name=bm,course_name=kc).delete()
            result['status'] = True
        return HttpResponse(json.dumps(result))
    else:
        return redirect('/')


@auth
def index_lt(request):
    result = {'message':[]}
    if request.session['type'] == 2:
        name = request.POST.get('name',None)
        user_name = request.session['user']
        obj = models.Chat_p.objects.filter(user_name=user_name,adviser_name=name).all()
        for i in obj:
            if i.status == '1':
                list_text = [i.user_name,i.message]
                result['message'].append(': '.join(list_text))
            else:
                list_text = [i.adviser_name, i.message]
                result['message'].append(': '.join(list_text))
        print(result)
        return HttpResponse(json.dumps(result))
    else:
        return redirect('/')


@auth
def index_tj(request):
    result = {'status':False,'message':''}
    if request.session['type'] == 2:
        if request.POST:
            data = request.POST.get('data',None)
            adviser_name = request.POST.get('name',None)
            name = request.session['user']
            school_id = request.session['school_id']
            print(data, adviser_name)
            models.Chat_p.objects.create(user_name=name,adviser_name=adviser_name,status=1,school_id=school_id,message=data)
            result['status'] = True
            return HttpResponse(json.dumps(result))
    else:
        return redirect('/')


@auth
def adviser_lt(request):
    result = {'message':[]}
    if request.session['type'] == 3:
        user_name = request.POST.get('name',None)
        name = request.session['user']
        obj = models.Chat_p.objects.filter(user_name=user_name,adviser_name=name).all()
        for i in obj:
            if i.status == '1':
                list_text = [i.user_name,i.message]
                result['message'].append(': '.join(list_text))
            else:
                list_text = [i.adviser_name, i.message]
                result['message'].append(': '.join(list_text))
        print(result)
        return HttpResponse(json.dumps(result))
    else:
        return redirect('/')


@auth
def adviser_tj(request):
    result = {'status':False,'message':''}
    if request.session['type'] == 3:
        if request.POST:
            data = request.POST.get('data',None)
            name = request.POST.get('name',None)
            adviser_name = request.session['user']
            school_id = request.session['school_id']
            print(data, adviser_name)
            models.Chat_p.objects.create(user_name=name,adviser_name=adviser_name,status=2,school_id=school_id,message=data)
            result['status'] = True
            return HttpResponse(json.dumps(result))
    else:
        return redirect('/')


@auth
def index_task(request):
    print('index_task')
    result = {'status': False, 'message': ''}
    if request.session['type'] == 2:
        xq = request.session['school_id']
        if request.POST:
            user_name = request.session['user']
            xq = request.session['school_id']
            user_select = request.POST.get('user_select')
            print(user_select,'22222222222')
            request.session['user_select'] = user_select
            g1 = models.UserInfo.objects.get(username=user_name,campus_id=xq)
            course_obj = g1.course_set.all()
            result['status'] = True
            return HttpResponse(json.dumps(result))
            # return render(request, 'index_task.html',{'course_obj':course_obj})
        else:
            user_name = request.session['user']
            g1 = models.UserInfo.objects.get(username=user_name, campus_id=xq)
            course_obj = g1.course_set.all()
            if request.session['user_select'] == False:
                if course_obj:
                    request.session['user_select'] = course_obj[0].name
                else:
                    return render(request, 'index_task.html', {'info_exist': False})
            course_id = models.Course.objects.filter(name=request.session['user_select'],campus_id=xq).all()[0].id
            print(course_id,'aaaaaaaaaaaaaaaaaa')
            kc_all = models.Course_content.objects.filter(course_id=course_id).count()
            current_page = request.GET.get('p1', 1)  # 获取GET请求的p数值 如过没有就设置为1
            # 每页显示10条数据
            # 第一页：0-10
            page_display_num = 3  # 每页显示多少行
            current_page = int(current_page)
            start = (current_page - 1) * page_display_num  # 计算出从数据库里取数据的开始下标
            end = current_page * page_display_num  # 计算出从数据库里取数据的结束下标
            # 将所有的页码显示在页面上
            total_item = models.Course_content.objects.filter(course_id=course_id).all().count()
            all_page, remainder = divmod(total_item, page_display_num)  # 计算分页的总页数 如过b不等于0那么all_page就要加1
            if remainder != 0:
                all_page = all_page + 1
            begin = 0
            end_num = 0
            if all_page > 6:  # 计算分页在web上显示的页数 分页显示5个
                all_num = all_page - 2
                if current_page > all_num:
                    begin = all_num - 3
                    end_num = all_num + 2
                elif current_page <= 2:
                    begin = 0
                    end_num = 5
                else:
                    begin = current_page - 3
                    end_num = current_page + 2
            else:
                begin = 0
                end_num = all_page
            list_page = []
            begin_page = "<a href='/index/task/?p1=1'>首页<a>"
            list_page.append(begin_page)
            if current_page == 1:
                prev = "<a href='#'>上一页<a>"
            else:
                prev = "<a href='/index/task/?p1=%s'>上一页<a>" % (current_page - 1)
            list_page.append(prev)
            for i in range(begin + 1, end_num + 1):
                if i == current_page:  # 当用户点击的是标签返回的就是那个GET请求p的数字 就选中这个标签
                    temp = "<a class='active' href='/index/task/?p1=%s' > %s<a>" % (i, i)
                else:
                    temp = "<a href='/index/task/?p1=%s'> %s<a>" % (i, i)
                list_page.append(temp)

            if current_page == all_page:
                down = "<a href='#'>下一页<a>"
            else:
                down = "<a href='/index/task/?p1=%s'>下一页<a>" % (current_page + 1)
            list_page.append(down)
            end_page = "<a href='/index/task/?p1=%s'>末页<a>" % all_page
            list_page.append(end_page)
            temp = ''.join(list_page)
            type_list = models.Course_content.objects.filter(course_id=course_id).all()[start:end]
            chat_list = []
            school_id = request.session.get('school_id', None)
            username = request.session.get('user', None)
            task_obj = models.Task.objects.filter(course_content_id__course__campus__id=school_id,username=username).values('course_content_id__name')
            for task_index in task_obj:
                print(task_index['course_content_id__name'])
                chat_list.append(task_index['course_content_id__name'])
            return render(request, 'index_task.html',{'course_obj':course_obj,'type_list':type_list,'str_page': mark_safe(temp),'all_page':all_page,'chat_list':chat_list,'info_exist':True})
    else:
        return redirect('/')

@auth
def index_submit(request):
    if request.session['type'] == 2:
        result = {'message':'','mark':''}
        username = request.session.get('user',None)
        task_name = request.POST.get('task_name',None)
        user_select = request.session.get('user_select',None)
        task_content = request.session.get('task_content',None)
        school_id =  request.session.get('school_id',None)
        obj = models.Task.objects.filter(course_content_id__course__name=user_select,username=username,course_content_id__name=task_name).all()
        if obj:
            print(task_name,user_select,username)
            result['message'] = obj[0].task_content
            result['mark'] = obj[0].mark
        return HttpResponse(json.dumps(result))
    else:
        return redirect('/')

@auth
def index_message(request):
    result = {'status':False}
    if request.session['type'] == 2:
        result = {'message':'','mark':''}
        username = request.session.get('user',None)
        task_name = request.POST.get('task_name',None)
        user_select = request.session.get('user_select',None)
        task_content = request.POST.get('task_content',None)
        school_id =  request.session.get('school_id',None)
        print('1111')
        print(task_content)
        print(task_name,user_select)
        obj = models.Task.objects.filter(course_content_id__name=task_name, username=username, course_content_id__course__name=user_select).all()
        if not obj:
            task_id = models.Course_content.objects.filter(course__campus__id=school_id,course__name=user_select,name=task_name).all()
            print(task_id[0].id)
            models.Task.objects.create(username=username,course_content_id_id=task_id[0].id,task_content=task_content)
            result['status'] = True
        return HttpResponse(json.dumps(result))
    else:
        return redirect('/')


@auth
def teacher_task(request):
    if request.session['type'] == 1:
        if request.POST:
            print('1111111111111111111111111111111111111')
            result = {'message': '', 'mark': ''}
            username = request.POST.get('user', None)
            task_name = request.POST.get('task_name', None)
            user_select = request.POST.get('user_select', None)
            school_id = request.session.get('school_id', None)
            obj = models.Task.objects.filter(course_content_id__course__name=user_select,course_content_id__course__campus_id=school_id,username=username
                                             ,course_content_id__name=task_name).all()
            if obj:
                print('2222222222222222222222222')
                result['message'] = obj[0].task_content
            return HttpResponse(json.dumps(result))
        else:
            xq = request.session['school_id']
            user_name = request.session['user']
            kc_all = models.Task.objects.filter(course_content_id__course__campus_id=xq).count()
            current_page = request.GET.get('p1', 1)  # 获取GET请求的p数值 如过没有就设置为1
            # 每页显示10条数据
            # 第一页：0-10
            page_display_num = 3  # 每页显示多少行
            current_page = int(current_page)
            start = (current_page - 1) * page_display_num  # 计算出从数据库里取数据的开始下标
            end = current_page * page_display_num  # 计算出从数据库里取数据的结束下标
            # 将所有的页码显示在页面上
            task_obj = models.Task.objects.exclude(mark__isnull=False).filter(course_content_id__course__campus_id=xq).values('username','course_content_id__name'
                                                                                                  ,'course_content_id__course__name'
                                                                                                  ,'task_content','mark')
            print(task_obj.count())
            total_item = task_obj.count()
            all_page, remainder = divmod(total_item, page_display_num)  # 计算分页的总页数 如过b不等于0那么all_page就要加1
            if remainder != 0:
                all_page = all_page + 1
            begin = 0
            end_num = 0
            if all_page > 6:  # 计算分页在web上显示的页数 分页显示5个
                all_num = all_page - 2
                if current_page > all_num:
                    begin = all_num - 3
                    end_num = all_num + 2
                elif current_page <= 2:
                    begin = 0
                    end_num = 5
                else:
                    begin = current_page - 3
                    end_num = current_page + 2
            else:
                begin = 0
                end_num = all_page
            list_page = []
            begin_page = "<a href='/teacher/task/?p1=1'>首页<a>"
            list_page.append(begin_page)
            if current_page == 1:
                prev = "<a href='#'>上一页<a>"
            else:
                prev = "<a href='/teacher/task/?p1=%s'>上一页<a>" % (current_page - 1)
            list_page.append(prev)
            for i in range(begin + 1, end_num + 1):
                if i == current_page:  # 当用户点击的是标签返回的就是那个GET请求p的数字 就选中这个标签
                    temp = "<a class='active' href='/teacher/task/?p1=%s' > %s<a>" % (i, i)
                else:
                    temp = "<a href='/teacher/task/?p1=%s'> %s<a>" % (i, i)
                list_page.append(temp)

            if current_page == all_page:
                down = "<a href='#'>下一页<a>"
            else:
                down = "<a href='/teacher/task/?p1=%s'>下一页<a>" % (current_page + 1)
            list_page.append(down)
            end_page = "<a href='/teacher/task/?p1=%s'>末页<a>" % all_page
            list_page.append(end_page)
            temp = ''.join(list_page)
            type_list = task_obj[start:end]
            chat_list = []
            return render(request, 'teacher_task.html',
                          { 'type_list': type_list, 'str_page': mark_safe(temp),
                           'all_page': all_page, 'chat_list': chat_list, 'info_exist': True})
    else:
        return redirect('/')


@auth
def teacher_submit(request):
    if request.session['type'] == 1:
        result = {'status':False}
        if request.POST:
            task_content = request.POST.get('task_content', None)
            user_select = request.POST.get('user_select', None)
            user = request.POST.get('user', None)
            task_name = request.POST.get('task_name', None)
            school_id = request.session.get('school_id')
            obj = models.Task.objects.exclude(mark__isnull=False).filter(course_content_id__name=task_name, username=user,
                                             course_content_id__course__name=user_select,course_content_id__course__campus_id=school_id).all()
            if obj:
                print('ok')
                models.Task.objects.exclude(mark__isnull=False).filter(course_content_id__name=task_name, username=user,
                                                                       course_content_id__course__name=user_select,
                                                                       course_content_id__course__campus_id=school_id).update(mark=task_content)
                result['status'] = True
            print(task_content,user_select,user,task_name)
        return HttpResponse(json.dumps(result))
    else:
        return redirect('/')