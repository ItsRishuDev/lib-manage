from xml.dom import NotFoundErr
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.hashers import make_password

from rest_framework import permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication
from knox.models import AuthToken

from .serializers import CreateUserSerializer
from account.models import MemberDetails
from account.serializers import (
    MemberDetailSerializer,
    ShowUserSerializer,
    UpdateMemberDetailSerializer,
)

# Create your views here.


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class RegisterAPI(LoginView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username", False)
        password = request.data.get("password", False)
        name = request.data.get("name", False)
        email = request.data.get("email", False)

        if username and password and name and email:
            user = User.objects.filter(username__iexact=username)
            if user.exists():
                return Response(
                    {
                        "status": False,
                        "response": "Username already exist",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                password = make_password(password)

                temp_data = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "first_name": name,
                }

                serializer = CreateUserSerializer(data=temp_data)

                if serializer.is_valid():
                    user = serializer.save()

                    token_ttl = self.get_token_ttl()
                    instance, token = AuthToken.objects.create(user, token_ttl)
                    user_logged_in.send(
                        sender=user.__class__, request=request, user=user
                    )

                    request.user = user
                    data = self.get_post_response_data(request, token, instance)
                    return Response(
                        {
                            "status": True,
                            "response": {"user_id": user.id, "token": data},
                        },
                        status=status.HTTP_201_CREATED,
                    )

                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

        else:
            return Response(
                {
                    "status": False,
                    "response": "Please provide name, username, email and password",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class MemberDetailView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get(self, request):
        memberDetails = MemberDetails.objects.all()
        serializer = MemberDetailSerializer(memberDetails, many=True)
        return Response(
            {"status": True, "response": serializer.data}, status=status.HTTP_200_OK
        )

    def post(self, request):
        user_id = request.data.get("user", False)
        try:
            user = User.objects.get(id=user_id)
            serializer = MemberDetailSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response(
                    {"status": True, "response": "Member details added successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response({"status": False, "response": serializer.errors})

        except User.DoesNotExist:
            return Response(
                {"status": False, "response": "User does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def patch(self, request):
        member_id = request.data.get("id")
        try:
            member = MemberDetails.objects.get(id=member_id)
            serializer = UpdateMemberDetailSerializer(member, request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"status": True, "response": "Member Details Updated"},
                    status=status.HTTP_202_ACCEPTED,
                )

            else:
                return Response(
                    {"status": False, "response": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except MemberDetails.DoesNotExist:
            return Response({"status": False, "response": "Member does not exist"}, 
            status=status.HTTP_400_BAD_REQUEST)


class ShowUserView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get(self, request):
        users = User.objects.all()
        serializer = ShowUserSerializer(users, many=True)
        return Response(
            {"status": True, "response": serializer.data}, status=status.HTTP_200_OK
        )
