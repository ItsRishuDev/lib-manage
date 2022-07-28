from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

import json

from rest_framework.test import APIClient
from rest_framework import status

from account.models import MemberDetails


client = APIClient()


class AccountAppTest(TestCase):
    def setUp(self):
        # Generating admin User
        admin_username = "anony"
        admin_password = "password"
        my_admin = User.objects.create_superuser(
            admin_username, "admin@test.com", admin_password
        )

        self.admin_credentials = {
            "username": admin_username,
            "password": admin_password,
        }

        admin_response = client.post(
            reverse("login_user"),
            data=json.dumps(self.admin_credentials),
            content_type="application/json",
        ).data

        self.admin_token = admin_response["token"]

        # Generating User object
        self.setup_payload = {
            "username": "rishabh",
            "password": "password",
            "name": "Rishabh",
            "email": "rishabh@rishabh.com",
        }

        self.user_response = client.post(
            reverse("register_user"),
            data=json.dumps(self.setup_payload),
            content_type="application/json",
        ).data
        self.user_token = self.user_response["response"]["token"]["token"]

        user_obj = User.objects.get(id=self.user_response["response"]["user_id"])
        # Generating Member Detail Object

        self.member_detail_obj = MemberDetails.objects.create(
            user=user_obj, phone=9876543210, member_type="Student"
        )

    # Registration Api Test Cases
    def test_create_valid_user(self):
        self.valid_payload = {
            "username": "test",
            "password": "password",
            "name": "test name",
            "email": "test@test.com",
        }

        response = client.post(
            reverse("register_user"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_missing_user(self):
        self.invalid_missing_field_payload = {"username": "test", "password": "test123"}

        response = client.post(
            reverse("register_user"),
            data=json.dumps(self.invalid_missing_field_payload),
            content_type="application/json",
        )
        self.assertEqual(response.data["status"], False)
        self.assertEqual(
            response.data["response"],
            "Please provide name, username, email and password",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_existing_username(self):
        self.invalid_existing_username_payload = {
            "username": "rishabh",
            "password": "thisispassword",
            "name": "Test 2",
            "email": "test@rishabh.com",
        }

        response = client.post(
            reverse("register_user"),
            data=json.dumps(self.invalid_existing_username_payload),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], False)
        self.assertEqual(response.data["response"], "Username already exist")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # User Test

    def test_show_all_user(self):
        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.get(reverse("view_user"), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_show_all_user(self):
        response = client.get(reverse("view_user"), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_invalid_user_show_all_user(self):
        client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = client.get(reverse("view_user"), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    # Create Member Detail Test 

    def test_create_member_detail(self):
        member_detail = {
            "user": self.user_response["response"]["user_id"],
            "phone": 9999999999,
            "issuedBook": 1,
            "member_type": "Student",
        }
        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.post(
            reverse("member_view"),
            data=json.dumps(member_detail),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], True)
        self.assertEqual(response.data["response"], "Member details added successfully")

    def test_invalid_user_create_member_detail(self):
        member_detail = {
            "user": self.user_response["response"]["user_id"]+100,
            "phone": 9999999999,
            "member_type": "Student",
        }
        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.post(
            reverse("member_view"),
            data=json.dumps(member_detail),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], False)
        self.assertEqual(response.data["response"], "User does not exist")

    def test_invalid_create_member_detail(self):
        member_detail = {
            "phone": 9999999999,
            "member_type": "Student",
        }
        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.post(
            reverse("member_view"),
            data=json.dumps(member_detail),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], False)

    # Update Member Detail Test 

    def test_update_member_detail(self):
        member_detail = {
            "id": self.member_detail_obj.id,
            "issuedBook": 1,
            "bookLimit": 3,
        }
        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.patch(
            reverse("member_view"),
            data=json.dumps(member_detail),
            content_type="application/json",
        )

        response_member_obj = MemberDetails.objects.get(id=self.member_detail_obj.id)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data["status"], True)
        self.assertEqual(response.data["response"], "Member Details Updated")
        self.assertEqual(response_member_obj.issuedBook, 1)
        self.assertEqual(response_member_obj.bookLimit, 3)

    def test_invalid_member_update_member_detail(self):
        member_detail = {
            "id": self.member_detail_obj.id + 100,
            "issuedBook": 1,
            "bookLimit": 3,
        }
        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.patch(
            reverse("member_view"),
            data=json.dumps(member_detail),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], False)
        self.assertEqual(response.data["response"], "Member does not exist")


    def test_invalid_update_member_detail(self):
        member_detail = {
            "id": self.member_detail_obj.id,
            "issuedBook": 'blah',
            "bookLimit": 3,
        }
        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.patch(
            reverse("member_view"),
            data=json.dumps(member_detail),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], False)
  

    # Show Member Details Test

    def test_show_all_member(self):
        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.get(reverse("member_view"), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_show_all_member(self):
        response = client.get(reverse("member_view"), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_invalid_user_show_all_member(self):
        client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = client.get(reverse("member_view"), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )