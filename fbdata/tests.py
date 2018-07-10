from django.test import TestCase
import json
import os
from timeit import default_timer as timer
from django.contrib.auth.models import User

from mysite.settings import BASE_DIR

from .models import *

class TestFileUpload(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='test_user',email='test@gmail.com',password='blahberg')
		login = self.client.login(username='test_user',password='blahberg')

		self.second_upload_message_path = os.path.join(BASE_DIR,r'fbdata/test_data/test_uploading_again.zip')
		self.large_message_path = os.path.join(BASE_DIR,r'fbdata/test_data/test_large_message_file.zip')
		self.multiple_message_path = os.path.join(BASE_DIR,r'fbdata/test_data/test_multiple_zip_messages.zip')

	def test_FileUpload_record_is_created(self):
		FileUploadCreator.create_file_upload(self.user,self.multiple_message_path)

		self.assertEqual(FileUpload.objects.count(),1)


class TestUploader(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='test_user',email='test@gmail.com',password='blahberg')
		login = self.client.login(username='test_user',password='blahberg')

		self.second_upload_message_path = os.path.join(BASE_DIR,r'fbdata/test_data/test_uploading_again.zip')
		self.large_message_path = os.path.join(BASE_DIR,r'fbdata/test_data/test_large_message_file.zip')
		self.multiple_message_path = os.path.join(BASE_DIR,r'fbdata/test_data/test_multiple_zip_messages.zip')

		upload_result = FileUploadCreator.create_file_upload(self.user,self.multiple_message_path)

		Uploader.upload_from_FileUpload_record(upload_result)


	def test_zip_uploader_properly_uploads_people(self):

		self.assertEqual(Person.objects.count(),4)

		self.assertEqual(Person.objects.filter(name="person0").count(),1)
		self.assertEqual(Person.objects.filter(name="person1").count(),1)

	def test_zip_uploader_properly_uploads_conversations(self):

		self.assertEqual(Conversation.objects.count(),3)

		self.assertEqual(Conversation.objects.filter(title="person1").count(),1)
		self.assertEqual(Conversation.objects.filter(title="person1, person3 and person2").count(),1)

	def test_zip_uploader_properly_uploads_messages(self):

		self.assertEqual(Message.objects.count(),44)

		self.assertEqual(Message.objects.filter(content="You are now connected on Messenger.").count(),1)
		self.assertEqual(Message.objects.filter(content="Oh man! I am sad to hear you can't make it. But I completely understand. Thanks for the well wishes. When you are in St. Louis don't hesitate to message me. We would love to see you").count(),1)	

	def test_zip_uploader_does_not_duplicate_entries(self):

		Uploader.upload_from_zip(self.multiple_message_path,self.user)

		self.assertEqual(Person.objects.count(),4)
		self.assertEqual(Conversation.objects.count(),3)
		self.assertEqual(Message.objects.count(),44)

	def test_user_is_added_to_conversation_and_message(self):

		self.assertEqual(Conversation.objects.filter(user=self.user).count(),3)
		self.assertEqual(Message.objects.filter(user=self.user).count(),44)

	# def test_zip_uploader_performance(self):

	# 	start = timer()
	# 	Uploader.upload_from_zip(self.large_message_path,self.user)
	# 	end = timer()

	# 	self.assertTrue(end-start < 7)

	def test_second_upload_only_uploads_recent_messages(self):

		Uploader.upload_from_zip(self.second_upload_message_path,self.user)

		self.assertEqual(Message.objects.count(),45)


class TestMessageGraphData(TestCase):

	def setUp(self):
		self.user = User.objects.create_user(username='test_user',email='test@gmail.com',password='blahberg')
		self.client.login(username='test_user',password='blahberg')

		self.multiple_message_path = os.path.join(BASE_DIR,r'fbdata/test_data/test_multiple_zip_messages.zip')
		self.large_message_path = os.path.join(BASE_DIR,r'fbdata/test_data/test_large_message_file.zip')
		self.large_multiple_message_path = os.path.join(BASE_DIR,r'fbdata/test_data/test_large_multiple_zip_messages.zip')

		Uploader.upload_from_zip(self.multiple_message_path,self.user)

		self.default_data = MessageGraph.get_message_data(self.user)

		self.num_bins=50
		self.max_convos=1
		self.configurable_data = MessageGraph.get_message_data(self.user,num_bins=self.num_bins,max_convos=self.max_convos)


	def test_all_conversations_available(self):
		self.assertEqual(len(self.default_data),3)

	def test_conversations_are_sorted(self):
		self.assertEqual(self.default_data[0]['key'],'person2')

	def test_default_num_of_bins(self):
		self.assertEqual(len(self.default_data[0]['values']),101)

	def test_limit_num_conversations(self):
		self.assertEqual(len(self.configurable_data),2)

	def test_num_of_bins_is_configurable(self):
		self.assertEqual(len(self.configurable_data[0]['values']),51)

	# def test_performance(self):
	# 	start = timer()
	# 	Uploader.upload_from_zip(self.large_message_path,self.user)
	# 	end = timer()

	# 	upload_time = end-start

	# 	start = timer()
	# 	MessageGraph.get_message_data(self.user)
	# 	end = timer()

	# 	fetch_time = end-start

	# 	if(fetch_time):
	# 		print("Upload time:%g Fetch time:%g" % (upload_time,fetch_time))
	# 	self.assertTrue(end-start < 1)






