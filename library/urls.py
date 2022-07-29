from django.urls import path
from library import views

urlpatterns = [
    path('', views.ShowBookView.as_view(), name='liberary_book'),
    path('books/', views.BookView.as_view(), name='book_view'),
    path('issues/', views.IssueBookView.as_view(), name='book_issue'),
    path('issuedbook/', views.UserIssuedBookView.as_view(), name='user_issued_book'),
    path('submissions/', views.SubmissionDetailView.as_view(), name='book_submission'),
    path('usersubmission/', views.UserSubmissionView.as_view(), name='user_submitted_book'),
]