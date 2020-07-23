from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import Topic, Course, Student, Order, User
from django.shortcuts import get_list_or_404, render
from django import forms
from .forms import OrderForm, InterestForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.

def index(request):
    top_list = Topic.objects.all().order_by('id')[:5]
    course_list = Course.objects.all().order_by('-price')[:5]
    return render(request, 'myapp/index.html', {'top_list': top_list, 'course_list': course_list})

    # Answer 2.C - Yes, we're passing course_list as 2nd context variable to display the top 5 courses
    # which have the highest price in descending order and whether a particular course is available
    # for everyone or not.

def about(request):
    return render(request, 'myapp/about.html')

# 4.C No, we are not passing any context variable here.
# 4.D Not Applicable


def detail(request, top_no):
    get_list_or_404(Topic, id=top_no)
    tp = Topic.objects.get(id=top_no)
    courses = Course.objects.filter(topic=top_no)
    return render(request, 'myapp/detail.html', {'tp': tp, 'courses': courses})

# 5.C we are passing 2 context variables.
# 5.D we are passing tp as variable for Topic model  and courses as a variable for Course model.

def courses(request):
    courlist = Course.objects.all().order_by('id')
    return render(request, 'myapp/courses.html', {'courlist': courlist})

def placeorder(request):
    msg = ''
    courlist = Course.objects.all()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if order.levels <= order.course.stages:
                if order.course.price > 150:
                    updated_price = order.course.discount()
                    print(updated_price)
                    order.discounted_price = updated_price
                order.save()
                msg = 'Your course has been ordered successfully.'
            else:
                msg = 'You exceeded the number of levels for this course.'
            return render(request, 'myapp/orderesponse.html/', locals())
    else:
        form = OrderForm()
    return render(request, 'myapp/placeorder.html/', {'form': form, 'msg':msg, 'courlist': courlist})

def coursedetail(request,cour_id):
    course = Course.objects.get(id=cour_id)
    course_list = Course.objects.all().order_by('-price')[:5]
    top_list = Topic.objects.all().order_by('id')[:10]
    if request.method == 'POST':
        form = InterestForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['interested']:
                course.interested = course.interested + 1
                course.save()
        return render(request, 'myapp/index.html', {'top_list': top_list,'course_list':course_list})

    else:
        form = InterestForm()
    return render(request, 'myapp/coursedetail.html', {'form': form,'course': course})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('myapp:myaccount'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        return render(request, 'myapp/login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse(('myapp:index')))

@login_required
def myaccount(request):
    if Student.objects.get(id=request.user.id):
        sid = Student.objects.filter(id=request.user.id)
        firstname = request.user.first_name
        lastname = request.user.last_name
        interest_list = sid.values_list('interested_in__name')
        order_list = sid.values_list('order__course__name')
        context = {'First_name': firstname,'Last_name': lastname, 'interested_list': interest_list,'order_list': order_list}
        return render(request, 'myapp/myaccount.html', context)
    else:
         context = "You are not a registered student!"
         return render(request, 'myapp/myaccount.html', context)


