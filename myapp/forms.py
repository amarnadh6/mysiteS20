from django import forms
from django.contrib.auth.forms import UserCreationForm
from myapp.models import Order, Student, User


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['student', 'order_date', 'course', 'levels']
        widgets = {'student': forms.RadioSelect,
                   'order_type': forms.SelectDateWidget}
        labels = {'student': 'Student name',
                  'Order_type': 'Order Date',
                  'course': 'Course name',
                  'levels': 'levels'}


class InterestForm(forms.Form):
    CHOICES = [(1, 'Yes'), (0, 'No')]
    interested = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, required=True)
    levels = forms.IntegerField(min_value=1, initial=1)
    comments = forms.CharField(widget=forms.Textarea, required=False)
    labels = {'interested': 'interested',
              'levels': 'levels',
              'comments': 'Additional Comments'}


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'city', 'school']


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input'}))

    class Meta:
        model = Student
        fields = ['username',
                  'email',
                  'first_name',
                  'last_name',
                  'city',
                  'school',
                  'interested_in',
                  'password1',
                  'password2',
                  ]

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.city = self.cleaned_data['city']
        user.school = self.cleaned_data['school']
        if commit:
            user.save()

        return user
