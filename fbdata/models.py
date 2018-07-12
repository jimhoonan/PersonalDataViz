from django.db import models
from django.utils import timezone
from datetime import datetime
from django.db.models import Max, Min, Count
from django.contrib.auth.models import User

import zipfile
import json
import math


def user_directory_path(instance,filename):
	return 'user_data/user_{0}/{1}'.format(instance.user.id, filename)

class Person(models.Model):
	name = models.CharField(max_length=200)

	def __str__(self):
		return self.name

class Conversation(models.Model):
	title = models.CharField(max_length=200)
	recipients = models.ManyToManyField(Person)
	user = models.ForeignKey(User,on_delete=models.CASCADE, null=True)

	def __str__(self):
		return self.title

class Message(models.Model):
	sender = models.ForeignKey(Person,on_delete=models.CASCADE)
	conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE)
	timestamp = models.DateTimeField()
	content = models.CharField(max_length=20000)
	user = models.ForeignKey(User,on_delete=models.CASCADE, null=True)

	def __str__(self):
		return '%s: %s' % (self.sender,self.content)

class FileUpload(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	timestamp = models.DateTimeField()
	uploaded_file = models.FileField(max_length=500,upload_to=user_directory_path)



class FileUploadCreator():

	def create_file_upload(user,file):
		time = timezone.make_aware(datetime.now(),timezone.get_current_timezone())
		return FileUpload.objects.create(user=user,timestamp=time,uploaded_file=file)

class Uploader():

	def validate_conversation_json(convo):
		return 'participants' in convo and 'title' in convo and 'messages' in convo

	def validate_message_json(message):
		return 'content' in message and 'sender_name' in message and 'timestamp' in message

	def get_latest_uploaded_message_in_conversation(convo):

		most_recent_message = timezone.make_aware(datetime.utcfromtimestamp(0),timezone.get_current_timezone())
		if(Message.objects.filter(conversation=convo).count() > 0):
			most_recent_message = Message.objects.filter(conversation=convo).aggregate(Max('timestamp'))['timestamp__max']

		return most_recent_message

	def create_messages_to_add(data,convo,recipient_lookup,most_recent_message):

		messages_to_add = []

		for m in data['messages']:
			if not Uploader.validate_message_json(m):
				continue

			time = datetime.utcfromtimestamp(m['timestamp'])
			aware_time = timezone.make_aware(time,timezone.get_current_timezone())

			if m['sender_name'] not in recipient_lookup:
				recipient_lookup[m['sender_name']] = Person.objects.get_or_create(name=m['sender_name'])[0]

			if aware_time > most_recent_message:
				messages_to_add.append(Message(content=m['content'],timestamp=aware_time,
					conversation=convo,sender=recipient_lookup[m['sender_name']],
					user=convo.user))

		return messages_to_add

	def upload_single_conversation_json(data,user):

		recipient_lookup ={}

		if not Uploader.validate_conversation_json(data):
			return

		convo = Conversation.objects.get_or_create(title=data['title'], user=user)[0]
		convo.save()

		for p in data['participants']:
			person= Person.objects.get_or_create(name=p)[0]
			recipient_lookup[p] = person
			convo.recipients.add(person)

		convo.save()

		most_recent_message = Uploader.get_latest_uploaded_message_in_conversation(convo)

		messages_to_add = Uploader.create_messages_to_add(data,convo,recipient_lookup,most_recent_message)

		Message.objects.bulk_create(messages_to_add)

	def upload_from_zip(f,user):
		zip_ref = zipfile.ZipFile(f,'r')

		for file in zip_ref.infolist():
			if file.filename[-12:] == 'message.json':
				text = zip_ref.read(file)
				data = json.loads(text)
				Uploader.upload_single_conversation_json(data,user)
	
	def upload_from_FileUpload_record(file_upload_record):
		Uploader.upload_from_zip(file_upload_record.uploaded_file,file_upload_record.user)


class MessageGraph():

	def bin_messages(messages, min_time, bin_size, num_bins):
		bin_count = [0 for x in range(num_bins + 1)]

		for m in messages:
			bin_count[math.floor((m.timestamp.timestamp() - min_time)/bin_size)] += 1

		result = []

		for i in range(len(bin_count)):
			result.append([(min_time + bin_size*i)*1000,bin_count[i]])

		return result 


	def get_message_data(user, num_bins=100, max_convos = 10):
		#[{key:name,"values":[[timestamp,count]...]...}


		conversations = Conversation.objects.filter(user=user)
		conversations = conversations.annotate(m_count=Count('message'),max_time=Max('message__timestamp'),min_time=Min('message__timestamp'))
		conversations = conversations.order_by('-m_count')
		agg = conversations.aggregate(Max('max_time'),Min('min_time'))
		result = []

		if(conversations.count() == 0):
			return result

		max_time= agg['max_time__max'].timestamp()
		min_time=agg['min_time__min'].timestamp()

		bin_size = (max_time - min_time)/num_bins
		others = []

		for i in range(len(conversations)):
			entry = {}
			current_message_bins = MessageGraph.bin_messages(Message.objects.filter(conversation = conversations[i]),min_time,bin_size,num_bins)
			if(i < max_convos):
				entry['key'] = conversations[i].title
				entry['values'] = current_message_bins
				result.append(entry)
			else:
				if(i == max_convos):
					others = current_message_bins
				else:
					for x in range(len(others)):
						others[x][1] += current_message_bins[x][1]
		
		if(len(others) > 0):
			result.append({'key':'Others','values':others})


		return result


