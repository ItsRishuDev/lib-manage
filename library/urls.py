from django.urls import path
from library import views

urlpatterns = [
    path('', views.ShowBookView.as_view()),
    path('books/', views.BookView.as_view()),
    path('issues/', views.IssueBookView.as_view()),
    path('issuedbook/', views.UserIssuedBookView.as_view()),
]