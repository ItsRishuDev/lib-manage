from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status

from library.models import Book, IssuedBook, SubmissionDetail
# Create your tests here.

# initialize the APIClient app
client = Client()