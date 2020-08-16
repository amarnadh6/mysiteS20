import string
from datetime import datetime
import random
from django.contrib.auth import (
    login as auth_login,
)
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordContextMixin
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView, FormView
from .models import Topic, Course, Student, Order, User
from django.shortcuts import get_list_or_404, render, resolve_url, redirect
from .forms import OrderForm, InterestForm, PasswordRequestForm, UserUpdateForm
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm


# Create your views here.

def index(request):
    if request.session.test_cookie_worked():
        print("Test cookie worked")
        request.session.delete_test_cookie()
        print("Test cookie deleted")
    else:
        print("Please enable cookies and try again.")

    top_list = Topic.objects.all().order_by('id')[:5]
    course_list = Course.objects.all().order_by('-price')[:5]
    lst_login = ''
    if 'last_login' in request.session:
        lst_login = request.session.get('last_login')
    else:
        HttpResponse("Your last login was more than one hour ago")
    return render(request, 'myapp/index.html',
                  {'top_list': top_list, 'course_list': course_list, 'lst_login': lst_login})

    # Answer 2.C - Yes, we're passing course_list as 2nd context variable to display the top 5 courses
    # which have the highest price in descending order and whether a particular course is available
    # for everyone or not.


def about(request):
    request.session.set_test_cookie()

    # Number of visits to this view, as counted in the session variable.
    about_visits = request.session.get('about_visits', 0)
    request.session['about_visits'] = about_visits + 1
    request.session.set_expiry(300)
    return render(request, 'myapp/about.html', {'about_visits': about_visits})


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
    return render(request, 'myapp/placeorder.html/', {'form': form, 'msg': msg, 'courlist': courlist})


def coursedetail(request, cour_id):
    course = Course.objects.get(id=cour_id)
    course_list = Course.objects.all().order_by('-price')[:5]
    top_list = Topic.objects.all().order_by('id')[:10]
    if request.method == 'POST':
        form = InterestForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['interested']:
                course.interested = course.interested + 1
                course.save()
        return render(request, 'myapp/index.html', {'top_list': top_list, 'course_list': course_list})

    else:
        form = InterestForm()
    return render(request, 'myapp/coursedetail.html', {'form': form, 'course': course})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                current_login = datetime.now()
                request.session['last_login'] = current_login.strftime("%d-%m-%Y %H:%M:%S")
                request.session.set_expiry(3600)
                # request.session.set_expiry(0)
                return HttpResponseRedirect(reverse('myapp:myaccount'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        return render(request, 'myapp/login.html')


@login_required
def user_logout(request):
    request.session.flush()
    return render(request, 'myapp/logout.html')


@login_required(login_url='/myapp/login')
def myaccount(request):
    sid = Student.objects.filter(id=request.user.id)
    if sid:
        firstname = request.user.first_name
        lastname = request.user.last_name
        interest_list = sid.values_list('interested_in__name')
        order_list = sid.values_list('order__course__name')
        context = {'First_name': firstname, 'Last_name': lastname, 'interested_list': interest_list,
                   'order_list': order_list}
        return render(request, 'myapp/myaccount.html', context)
    else:
        context = "You are not a registered student!"
        return render(request, 'myapp/myaccount.html', context)

def register(response):
    if response.method == "POST":
        form = UserRegistrationForm(response.POST)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.password = make_password(form.cleaned_data['password1'])
            form.save()
        return redirect('myapp:index')
    else:
        form = UserRegistrationForm()
    return render(response, "myapp/register.html", {"form": form})


def forgot_password(request):
    if request.method == 'POST':
        form = PasswordRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            last_name = form.cleaned_data['last_name']
            first_name = form.cleaned_data['first_name']
            letters_and_digits = string.ascii_letters + string.digits
            random_pass = ''.join(random.choice(letters_and_digits) for i in range(8))
            user = User.objects.get(last_name=last_name, first_name=first_name)
            user.set_password(random_pass)
            user.save()
            subject = "Password Recovery"
            from_email = "bookstore@gmail.com"
            to_email = [email]
            msg1 = "This email is for password recovery. The new password is: "
            msg2 = random_pass
            msg3 = " You can Log In here: http://127.0.0.1:8000/myapp/login/"
            signup_message = msg1 + msg2 + msg3
            send_mail(subject=subject, from_email=from_email, recipient_list=to_email, message=signup_message,
                      fail_silently=False)
            return render(request, 'myapp/forgot_password_done.html')
        else:
            return render(request, 'myapp/forgot_password.html', {'form': form})

    else:
        form = PasswordRequestForm()
        return render(request, 'myapp/forgot_password.html', {'form': form})


class PasswordResetView(PasswordContextMixin, FormView):
    email_template_name = 'registration/password_reset_email.html'
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = None
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    template_name = 'registration/password_reset_form.html'
    title = _('Password reset')
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)


INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'


class PasswordResetConfirmView(PasswordContextMixin, FormView):
    form_class = SetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    reset_url_token = 'set-password'
    success_url = reverse_lazy('password_reset_complete')
    template_name = 'registration/password_reset_confirm.html'
    title = _('Enter new password')
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token)
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    @staticmethod
    def get_user(uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': _('Password reset unsuccessful'),
                'validlink': False,
            })
        return context


class PasswordResetCompleteView(PasswordContextMixin, TemplateView):
    template_name = 'registration/password_reset_complete.html'
    title = _('Password reset complete')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = resolve_url(settings.LOGIN_URL)
        return context


class PasswordChangeView(PasswordContextMixin, FormView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'registration/password_change_form.html'
    title = _('Password change')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)


class PasswordChangeDoneView(PasswordContextMixin, TemplateView):
    template_name = 'registration/password_change_done.html'
    title = _('Password change successful')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
