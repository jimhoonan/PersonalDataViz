from django.contrib import admin

from .models import Person, Conversation, Message, FileUpload

admin.site.register(Person)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(FileUpload)