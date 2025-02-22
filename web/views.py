import markdown
from django.shortcuts import render
from django.http import JsonResponse
from django.http.response import HttpResponseNotAllowed
from datetime import timedelta
from .models import User, Chat
from .utils import convert_to_matrix, travelling_salesman, get_route_instructions
from .utils import random_session, chatbot_response

md = markdown.Markdown(extensions=["fenced_code"])

def home(request):
    session = request.session.get('sess_id', random_session())
    request.session['sess_id'] = session
    request.session.set_expiry(timedelta(days=7))

    return render(request, 'home.html')

def chatinput(request):
    input = request.POST.get('input')
    if not input:
        return JsonResponse({'error': 'Input not provided.'})
    session = request.session.get('sess_id', None)
    if not session:
        return JsonResponse({'error': 'Session not found.'})
    
    user = User.objects.filter(session_id=session).last()
    if not user:
        user = User(session_id=session)
    user.save()

    chat = Chat(user=user, session_id=session, message=input, type='user')
    chat.save()
    history = Chat.objects.filter(user=user).order_by('created_at')
    stops = user.stops

    assistant = chatbot_response(input=input, history_obj=history, route=stops)
    chat = Chat(user=user, session_id=session, message=assistant, type='assistant')
    chat.save()
    
    return JsonResponse({'assistant': assistant})

def chatdata(request):
    session = request.session.get('sess_id', None)
    if not session:
        return JsonResponse({'error': 'Session not found.'})
    user = User.objects.filter(session_id=session).last()
    if not user:
        return JsonResponse({'error': 'User not found.'})
    chats = Chat.objects.filter(user=user).order_by('created_at')
    data = []
    for chat in chats:
        data.append({
            'message': md.convert(chat.message),
            'type': chat.type
        })
    return JsonResponse(data, safe=False)

def input(request):
    session = request.session.get('sess_id', None)
    if not session:
        return JsonResponse({'error': 'Session not found.'})
    try:
        start = request.POST.get('start_stop').split(',')
    except:
        return JsonResponse({'error': 'Start/Stop location not provided.'})
    
    data = [ [start[0],float(start[1]),float(start[2])] ]
    i = 1
    for name, value in request.POST.items():
        if name == 'start_stop' or not value:
            continue
        value = value.split(',')
        data.append([value[0],float(value[1]),float(value[2])])
        i += 1
    
    mat = convert_to_matrix(data)
    total_dist, route = travelling_salesman(mat)
    if total_dist == 9999:
        total_dist = 0
    result = []
    stops = []
    for i in range(len(route)-1):
        stops.append(data[route[i]])
        result.append(data[route[i]][0])
        result.append(str(round(mat[route[i]][route[i+1]])) + ' km')
    result.append(start[0])
    stops.append(data[0])

    user = User.objects.filter(session_id=session).last()
    if not user:
        user = User(session_id=session)
    user.route = result
    user.stops = stops
    user.distance = total_dist
    user.save()

    if result:
        chats = Chat.objects.filter(user=user).order_by('created_at')
        chat = chatbot_response(route=stops, history_obj=chats)
        if chat:
            chat_data = Chat(user=user, session_id=session, message=chat, type='assistant')
            chat_data.save()
        response = {'data': result, 'total_distance': (str(round(total_dist)) + ' km'),
                        'chat': md.convert(chat), 'instructions': get_route_instructions(stops)}
        return JsonResponse(response,safe=False)
    return JsonResponse({'error': 'No route found.'})
