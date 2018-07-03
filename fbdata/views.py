from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe

from .forms import UploadFileForm
from .models import Uploader, MessageGraph

import json

def home(request):
	return render(request,'fbdata/home.html')

@login_required
def uploader(request):
	if request.method == 'POST' and request.FILES['myfile']:
		myfile = request.FILES['myfile']
		Uploader.upload_from_zip(myfile,request.user)
	return render(request, 'fbdata/uploader.html')

def graph(request):
	data = MessageGraph.get_message_data(request.user)
	if(len(data) > 0):
		return render(request,'fbdata/graph.html',{'data':mark_safe(json.dumps(data))})
	else:
		return render(request,'fbdata/no_data.html')



		

