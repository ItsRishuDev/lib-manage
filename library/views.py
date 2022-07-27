from tkinter import S
from django.shortcuts import render
from django.contrib.auth.models import User
from account.models import MemberDetails
from account.serializers import UpdateMemberDetailSerializer
from library import serializers

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from knox.auth import TokenAuthentication

from library.models import Book, IssuedBook, SubmissionDetail
from library.serializers import (
    BookSerializer,
    IssuedBookSerializer,
    SubmissionDetailSerializer,
    ShowIssuedBookSerializer
)

# Create your views here.


class BookView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": True, "response": "Books created successfully."},
                status=status.HTTP_201_CREATED,
            )

        else:
            return Response(
                {"status": False, "response": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def patch(self, request):
        book_id = request.data.get("id", False)
        try:
            book = Book.objects.get(id=book_id)
            serializer = BookSerializer(book, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"status": True, "response": "Book details updated"},
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                return Response(
                    {"status": False, "response": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Book.DoesNotExist:
            return Response(
                {"status": False, "response": "Book does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ShowBookView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        book = Book.objects.all()
        serializer = BookSerializer(book, many=True)
        return Response(
            {"status": True, "response": serializer.data}, status=status.HTTP_200_OK
        )


class IssueBookView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get(self, request):
        issuedBook = IssuedBook.objects.all()
        serializer = ShowIssuedBookSerializer(issuedBook, many=True)
        return Response(
            {"status": True, "response": serializer.data}, status=status.HTTP_200_OK
        )

    def post(self, request):
        book_id = request.data.get("book", False)
        user_id = request.data.get("user", False)
        force = request.data.get("force")

        try:
            book = Book.objects.get(id=book_id)

            try:
                user = User.objects.get(id=user_id)

                member = MemberDetails.objects.get(user=user)
                totalBookIssued = member.issuedBook

                if totalBookIssued < member.bookLimit or force is not None:
                    temp_data = {"issuedBook": totalBookIssued + 1}

                    serializer = IssuedBookSerializer(data=request.data)

                    if serializer.is_valid():
                        member_serializer = UpdateMemberDetailSerializer(member, data=temp_data)
                        if member_serializer.is_valid():
                            serializer.save(book=book, user=user)
                            member_serializer.save()
                            return Response(
                                {"status": True, "response": "Book Issued"},
                                status=status.HTTP_201_CREATED,
                            )

                        else:
                            return Response(
                                {"status": False, "response": member_serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                    else:
                        return Response(
                            {"status": False, "response": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                else:
                    return Response(
                        {
                            "status": False,
                            "response": "User has reached maximum book issue limit. Use force to issue book forcefully Or Increase Book Issue limit of user.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except User.DoesNotExist:
                return Response(
                    {"status": False, "response": "User does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Book.DoesNotExist:
            return Response(
                {"status": False, "response": "Book does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def patch(self, request):
        issue_id = request.data.get("id", False)
        returned = request.data.get("returned")

        try:
            issueBook = IssuedBook.objects.get(id=issue_id)
            print("___________________")
            print("Here 1")
            issue_data = {
                'user':issueBook.user.id,
                'book':issueBook.book.id,
                'returned':returned
            }
            serializer = IssuedBookSerializer(issueBook, data=issue_data)
            if serializer.is_valid():
                print("Here 2")
                #If User returns the book updating its Issue Book detail from Member Details. 
                if returned == 'true':
                    user = issueBook.user
                    member =  MemberDetails.objects.get(user=user)
                    bookIssued = int(member.issuedBook) - 1

                    tempData = {
                        'issuedBook':bookIssued
                    }

                    member_serializer = UpdateMemberDetailSerializer(member, data=tempData)
                    if member_serializer.is_valid():
                        print("here 3")
                        #Generating Submission Report, should apply pannelty or not.
                        submissionData = {
                            'user':user.id,
                            'issued_book':issueBook.book.id
                        }

                        submission_serializer = SubmissionDetailSerializer(data=submissionData)
                        if submission_serializer.is_valid():
                            submission_serializer.save()
                        else:
                            return Response({
                                'status':False,
                                'response':submission_serializer.errors
                            }, status=status.HTTP_400_BAD_REQUEST)    
                        
                        member_serializer.save()

                    else:
                        return Response({
                            'status':False,
                            'response':member_serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)    

                serializer.save()
                return Response(
                    {"status": True, "response": "Data updated successfully"},
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                return Response({
                    'status':False,
                    'response':serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)    

        except IssuedBook.DoesNotExist:
            return Response(
                {"status": False, "response": "Issued book not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class UserIssuedBookView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        books = IssuedBook.objects.filter(user=request.user, returned=False)
        serializer = ShowIssuedBookSerializer(books, many=True)
        return Response(
            {"status": True, "response": serializer.data}, status=status.HTTP_200_OK
        )

class UserSubmissionView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        submissions = SubmissionDetail.objects.filter(user=request.user)
        serializer = SubmissionDetailSerializer(submissions, many=True)
        return Response(
            {"status": True, "response": serializer.data}, status=status.HTTP_200_OK
        )        

class SubmissionDetailView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get(self, request):
        submissions = SubmissionDetail.objects.all()
        serializer = SubmissionDetailSerializer(submissions, many=True)
        return Response(
            {"status": True, "response": serializer.data}, status=status.HTTP_200_OK
        ) 
