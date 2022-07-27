from django.contrib import admin
from library.models import Book, IssuedBook, SubmissionDetail
# Register your models here.
admin.site.register(Book)
admin.site.register(IssuedBook)
admin.site.register(SubmissionDetail)