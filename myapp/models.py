from django.db import models
import datetime
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.timezone import now
from PIL import Image


class Topic(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=80, null=True, blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    topic = models.ForeignKey(Topic, related_name='courses', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[
        MaxValueValidator(200),
        MinValueValidator(100)
    ])
    for_everyone = models.BooleanField(default=True)
    hours = models.IntegerField(default=1)
    description = models.TextField(max_length=300, null=True, blank=True)
    interested = models.PositiveIntegerField(default=0)
    stages = models.PositiveIntegerField(default=3)
    comments = models.TextField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.name

    def discount(self):
        discounted_price = self.price - (self.price * Decimal(0.10))
        return discounted_price


class Student(User):
    CITY_CHOICES = [('WS', 'Windsor'), ('CG', 'Calgary'), ('MR', 'Montreal'), ('VC', 'Vancouver')]
    school = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=2, choices=CITY_CHOICES, default='WS')
    interested_in = models.ManyToManyField(Topic)
    # picture = models.ImageField(
    #     upload_to='myapp/profile_pics',
    #     blank=True, null=True,
    #     default='myapp/profile_pics/kavish.jpg'
    # )

    def __str__(self):
        return self.first_name


class Order(models.Model):
    VALID_VALUES = [(0, 'Cancelled'), (1, 'Order Confirmed')]
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    levels = models.PositiveIntegerField()
    order_status = models.IntegerField(choices=VALID_VALUES, default=1)
    order_date = models.DateTimeField(default=now, editable=True)
    discounted_price = models.FloatField(max_length=4, default=0)

    def __str__(self):
        return str(self.order_status)

    def total_cost(self):
        total = 0
        for course in Order.objects.all()['course']:
            total += course.price
        return total


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(default='profile_pics/default.png', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self):
        super().save()
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
