from django.shortcuts import render, redirect
from .models import Message

# Create your views here.

def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            request.session['chat_username'] = username
            return redirect('chat_room')
    return render(request, 'chat/index.html')

def chat_room(request):
    if 'chat_username' not in request.session:
        return redirect('chat_index')
    
    username = request.session['chat_username']
    messages = Message.objects.order_by('-timestamp')[:50]
    return render(request, 'chat/room.html', {
        'username': username,
        'messages': messages
    })
