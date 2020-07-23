from django import forms
from myapp.models import Order

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
    CHOICES = [('Yes', 1), ('No', 0)]
    interested = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, required=True)
    levels = forms.IntegerField(min_value=1, initial=1)
    comments = forms.CharField(widget=forms.Textarea, required=False)
    labels = {'interested': 'interested',
              'levels': 'levels',
              'comments': 'Additional Comments'}




