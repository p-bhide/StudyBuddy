from django.contrib import admin
from .models import Room, Message, Topic, User

# Register your models here.

admin.site.register([Room, Message, Topic, User])