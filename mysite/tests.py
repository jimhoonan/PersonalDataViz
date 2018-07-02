from django.contrib.auth.models import User

from django.test import TestCase
from .forms import SignUpForm


class TestAccountCreation(TestCase):

	def setUp(self):
		self.credentials = {'username':'hello','password':'blahberg','email':'hello@gmail.com'}
		self.form_data = {
			'username':self.credentials['username'],
			'email':self.credentials['email'],
			'password1':self.credentials['password'],
			'password2':self.credentials['password']}

	def test_SignUpForm(self):
		form = SignUpForm(data=self.form_data)

		self.assertTrue(form.is_valid())

	def test_sign_up(self):

		response = self.client.post('/signup/',self.form_data,follow=True)

		self.assertEqual(response.status_code,200)
		self.assertEqual(User.objects.count(),1)

	def test_multiple_sign_up(self):

		response = self.client.post('/signup/',self.form_data,follow=True)

		self.assertEqual(response.status_code,200)
		self.assertEqual(User.objects.count(),1)

		response = self.client.post('/signup/',self.form_data,follow=True)

		self.assertEqual(response.status_code,200)
		self.assertEqual(User.objects.count(),1)

class TestLogIn(TestCase):

	def setUp(self):

		self.credentials = {'username':'hello','password':'blahberg','email':'hello@gmail.com'}
		User.objects.create_user(username=self.credentials['username'],
			email=self.credentials['email'],
			password=self.credentials['password'])

	def test_login(self):

		response = self.client.post('/login/',self.credentials,follow=True)

		print(response.content)

		self.assertEqual(response.status_code,200)
		self.assertContains(response,'home')
		self.assertTrue(response.context['user'].is_authenticated)

