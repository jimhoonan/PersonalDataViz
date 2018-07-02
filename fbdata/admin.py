from django.contrib import admin

from .models import Person, Conversation, Message

admin.site.register(Person)
admin.site.register(Conversation)
admin.site.register(Message)