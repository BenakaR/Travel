from django.urls import path
from .views import home, input, chatdata, chatinput

urlpatterns = [
    path('', home, name='home'),
    path('input', input, name='input'),
    path('chatinput', chatinput, name='chatinput'),
    path('chathistory', chatdata, name='chathistory'),
]
