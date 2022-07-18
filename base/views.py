from array import array
from asyncio.windows_events import NULL
from pydoc import pager
import re
from unicodedata import name
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.db.models import Q, Count
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm
# Create your views here.

def loginpage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        user = request.POST.get('user')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=user)
        except:
            messages.error(request, 'User Doesnt exist')
        
        user = authenticate(request, username=user, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'username or password doesn\'t match')

    context = {'page' : page}
    return render(request, 'base/login_register.html', context)

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured while registering')

    return render(request, 'base/login_register.html', {'form':form})


def logoutpage(request):
    logout(request)
    return redirect('home')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__topic__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    topics = Topic.objects.all()
    # topics = Topic.objects.annotate(num=Count('room'))
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__topic__icontains=q))[:5]
    context = { 
        'rooms' : rooms,
        'topics' : topics,
        'room_count' : room_count,
        'room_messages' : room_messages,
        }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('updated')
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=pk)

    context = {
        'room' : room,
        'room_messages' : room_messages,
        'participants' : participants
        }
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(pk=pk)
    room = user.room_set.all()
    room_messages = user.message_set.all()
    topics = []
    for msg in room_messages:
        if msg.room.topic not in topics:
            topics.append(msg.room.topic)
    topics.sort(key=lambda x : x.topic)
    context = {
        'user' : user,
        'rooms' : room,
        'room_messages' : room_messages,
        'topics' : topics,
    }
    return render(request, 'base/userprofile.html', context)


@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm
    topics = Topic.objects.all()
    context = {
        'form' : form,
        'topics' : topics
        }

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(topic=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')

    return render(request, 'base/create-room.html', context)


@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance = room)
    topics = Topic.objects.all()

    context = {'form' : form, 'topics' :topics, 'room' : room, }

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(topic=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    return render(request, 'base/create-room.html', context)


@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' : room})


@login_required(login_url='/login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user :
        return HttpResponse('You are not allowed here')
    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' : message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    context={
        'user' : user,
        'form' : form,
    }
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user', pk=user.id)

    return render(request, 'base/update-user.html', context)