from django.contrib import admin
from django.db import models
from django.db.models.functions import Upper
from .models import Topic, Course, Student, Order
from django.utils.safestring import mark_safe
from django.utils.html import format_html


def add_50_to_hours(modeladmin, request, queryset):
    for course in queryset:
        course.hours += 10
        course.save()
    add_50_to_hours.short_description = 'Increase hours by 10'


def upper_case_name(modeladmin, request, queryset):
    st = Student()
    for st in queryset:
        st.first_name = st.first_name.upper()
        st.last_name = st.last_name.upper()
        st.save()
    upper_case_name.short_description = 'Student Full Name'


class CourseAdmin(admin.ModelAdmin):
    fields = ('name', 'topic', 'price', 'hours', 'for_everyone', 'comments')
    list_display = ('name', 'topic', 'price', 'hours', 'for_everyone', 'comments')
    actions = [add_50_to_hours]


def user_info(obj):
    return obj.description


class StudentAdmin(admin.ModelAdmin):
    fields = [('first_name', 'last_name'), 'city', 'school', 'interested_in', 'picture']
    list_display = ('first_name', 'last_name', 'city', 'school', 'picture')
    actions = [upper_case_name]


# Register your models here.


admin.site.register(Topic)
admin.site.register(Course, CourseAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Order)
