from urllib import request
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

import json

from rest_framework.test import APIClient
from rest_framework import status

from library.models import Book, IssuedBook
from account.models import MemberDetails

client = APIClient()


class LibraryAppTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Generating admin User

        cls.admin_username = "anony"
        cls.admin_password = "password"
        cls.admin_user = User.objects.create_superuser(
            cls.admin_username, "admin@test.com", cls.admin_password
        )

        cls.admin_credentials = {
            "username": cls.admin_username,
            "password": cls.admin_password,
        }

        cls.admin_response = client.post(
            reverse("login_user"),
            data=json.dumps(cls.admin_credentials),
            content_type="application/json",
        ).data

        cls.admin_token = cls.admin_response["token"]

        # Generating User object
        cls.setup_payload = {
            "username": "rishabh",
            "password": "password",
            "name": "Rishabh",
            "email": "rishabh@rishabh.com",
        }

        cls.user_response = client.post(
            reverse("register_user"),
            data=json.dumps(cls.setup_payload),
            content_type="application/json",
        ).data
        cls.user_token = cls.user_response["response"]["token"]["token"]

        cls.book_obj_1 = Book.objects.create(
            name="Book 1", author="Author 1", edition=1, price=400, late_fee=3
        )
        cls.book_obj_2 = Book.objects.create(
            name="Book 2", author="Author 2", edition=2, price=500, late_fee=4
        )
        cls.book_obj_3 = Book.objects.create(
            name="Book 3", author="Author 3", edition=1, price=600, late_fee=5
        )

        cls.user_obj = User.objects.get(id=cls.user_response["response"]["user_id"])

        cls.member_detail_obj = MemberDetails.objects.create(
            user=cls.user_obj,
            phone=9876543210,
            member_type="Student",
            bookLimit=3,
            issuedBook=1,
        )

        cls.issued_book_obj = IssuedBook.objects.create(
            user=cls.user_obj, book=cls.book_obj_1
        )

    # def setUp(self):
    #     self.book_obj_1 = Book.objects.create(
    #         name="Book 1", author="Author 1", edition=1, price=400, late_fee=3
    #     )
    #     self.book_obj_2 = Book.objects.create(
    #         name="Book 2", author="Author 2", edition=2, price=500, late_fee=4
    #     )
    #     self.book_obj_3 = Book.objects.create(
    #         name="Book 3", author="Author 3", edition=1, price=600, late_fee=5
    #     )

    #     self.user_obj = User.objects.get(id=self.user_response["response"]["user_id"])

    #     self.member_detail_obj = MemberDetails.objects.create(
    #         user=self.user_obj, phone=9876543210, member_type="Student", bookLimit=3, issuedBook=1
    #     )

    #     self.issued_book_obj = IssuedBook.objects.create(
    #         user=self.user_obj, book=self.book_obj_1
    #     )

    # Book Create Api Test Cases
    def test_create_valid_book(self):
        self.valid_payload = {
            "name": "Test Book",
            "author": "Test Author",
            "edition": 1,
            "price": 800,
            "late_fee": 5,
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.post(
            reverse("book_view"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["response"], "Books created successfully.")

    def test_create_invalid_book(self):
        self.valid_payload = {
            "author": "Test Author",
            "edition": "1st Edition",
            "price": "800",
            "late_fee": "5",
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.post(
            reverse("book_view"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_forbidden_book(self):
        self.valid_payload = {
            "name": "Test Book",
            "author": "Test Author",
            "edition": "1st Edition",
            "price": "800",
            "late_fee": "5",
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = client.post(
            reverse("book_view"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    def test_create_unauthorized_book(self):
        self.valid_payload = {
            "name": "Test Book",
            "author": "Test Author",
            "edition": "1st Edition",
            "price": "800",
            "late_fee": "5",
        }

        client.credentials()
        response = client.post(
            reverse("book_view"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    # Book Update Test Cases

    def test_update_valid_book(self):
        name = "Updated Book"
        author = "Updated Author"
        edition = 2
        price = 900
        late_fee = 7
        self.valid_payload = {
            "id": self.book_obj_1.id,
            "name": name,
            "author": author,
            "edition": edition,
            "available": False,
            "price": price,
            "late_fee": late_fee,
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.patch(
            reverse("book_view"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.updated_book = Book.objects.get(id=self.book_obj_1.id)

        self.assertEqual(response.data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data["response"], "Book details updated")
        self.assertEqual(self.updated_book.available, False)
        self.assertEqual(self.updated_book.price, price)
        self.assertEqual(self.updated_book.late_fee, late_fee)

    def test_update_invalid_book(self):
        name = "Updated Book"
        author = "Updated Author"
        edition = 2
        price = 900
        late_fee = 7
        self.invalid_payload = {
            "name": name,
            "author": author,
            "edition": edition,
            "available": False,
            "price": price,
            "late_fee": late_fee,
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.patch(
            reverse("book_view"),
            data=json.dumps(self.invalid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], False)
        self.assertEqual(response.data["response"], "Book does not exist.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_invalid_error_book(self):
        self.valid_payload = {
            "id": self.book_obj_1.id,
            "edition": "2nd edition",
            "available": False,
            "price": 200,
            "late_fee": 2,
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.patch(
            reverse("book_view"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Show Book Test Cases
    def test_view_valid_book(self):
        client.credentials()
        response = client.get(
            reverse("liberary_book"),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Create Issue Book Test Cases
    def test_create_valid_issue_book(self):
        self.valid_payload = {
            "user": self.user_response["response"]["user_id"],
            "book": self.book_obj_1.id,
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.post(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], True)
        self.assertEqual(response.data["response"], "Book Issued")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_valid_limit_reached_issue_book(self):
        self.valid_payload_1 = {
            "user": self.user_response["response"]["user_id"],
            "book": self.book_obj_1.id,
        }

        self.valid_payload_2 = {
            "user": self.user_response["response"]["user_id"],
            "book": self.book_obj_2.id,
        }

        self.valid_payload_3 = {
            "user": self.user_response["response"]["user_id"],
            "book": self.book_obj_3.id,
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)

        client.post(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload_1),
            content_type="application/json",
        )

        client.post(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload_2),
            content_type="application/json",
        )

        response = client.post(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload_2),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], False)
        self.assertEqual(
            response.data["response"],
            "User has reached maximum book issue limit. Use force to issue book forcefully Or Increase Book Issue limit of user.",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_book_issue_book(self):
        self.valid_payload = {
            "user": self.user_response["response"]["user_id"],
            "book": self.book_obj_1.id + 100,
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.post(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], False)
        self.assertEqual(response.data["response"], "Book does not exist")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_user_issue_book(self):
        self.valid_payload = {
            "user": self.user_response["response"]["user_id"] + 100,
            "book": self.book_obj_1.id,
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.post(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], False)
        self.assertEqual(response.data["response"], "User does not exist")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_issue_book(self):
        self.valid_payload = {
            "user": self.user_response["response"]["user_id"],
            "book": self.book_obj_1.id,
            "returned": "Nahi",
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.post(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_unauthorized_issue_book(self):
        self.valid_payload = {
            "user": self.user_response["response"]["user_id"],
            "book": self.book_obj_1.id,
        }

        client.credentials()
        response = client.post(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_create_invalid_forbidden_issue_book(self):
        self.valid_payload = {
            "user": self.user_response["response"]["user_id"],
            "book": self.book_obj_1.id,
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = client.post(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    # Show Issued Book Test Cases

    def test_view_valid_issued_book(self):
        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.get(
            reverse("book_issue"),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_invalid_forbidden_book(self):
        client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = client.get(
            reverse("book_issue"),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    def test_view_invalid_unauthorized_issued_book(self):
        client.credentials()
        response = client.get(
            reverse("book_issue"),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    # User Issued Book Test Cases
    def test_view_valid_user_issued_book(self):
        client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = client.get(
            reverse("user_issued_book"),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_invalid_unauthorized_user_issued_book(self):
        client.credentials()
        response = client.get(
            reverse("user_issued_book"),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    # Update Issue Book Test Cases
    def test_update_valid_issue_book(self):
        self.valid_payload = {
            "id": self.issued_book_obj.id,
            "returned": "true",
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.patch(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        updated_member_obj = MemberDetails.objects.get(user=self.user_obj.id)

        self.assertEqual(response.data["status"], True)
        self.assertEqual(response.data["response"], "Data updated successfully")
        self.assertEqual(
            updated_member_obj.issuedBook, self.member_detail_obj.issuedBook - 1
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_not_found_issue_book(self):
        self.valid_payload = {
            "id": self.issued_book_obj.id + 100,
            "returned": "true",
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.patch(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], False)
        self.assertEqual(response.data["response"], "Issued book not found")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_invalid_issue_book(self):
        self.valid_payload = {
            "id": self.issued_book_obj.id,
            "returned": "invalid",
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.patch(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_invalid_unauthorized_issue_book(self):
        self.valid_payload = {
            "id": self.issued_book_obj.id,
            "returned": "true",
        }

        client.credentials()
        response = client.patch(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_update_invalid_forbidden_issue_book(self):
        self.valid_payload = {
            "id": self.issued_book_obj.id,
            "returned": "true",
        }

        client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = client.patch(
            reverse("book_issue"),
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    # Submission Book Test Cases
    def test_view_valid_submission_book(self):
        client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token)
        response = client.get(
            reverse("book_submission"),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_invalid_unauthorized_submission_book(self):
        client.credentials()
        response = client.get(
            reverse("book_submission"),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_view_invalid_forbidden_submission_book(self):
        client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = client.get(
            reverse("book_submission"),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    # User Submission Book Test Cases
    def test_view_valid_user_submission_book(self):
        client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = client.get(
            reverse("user_submitted_book"),
            content_type="application/json",
        )

        self.assertEqual(response.data["status"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_invalid_user_submission_book(self):
        client.credentials()
        response = client.get(
            reverse("user_submitted_book"),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
