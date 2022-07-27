from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from main.settings import BOOK_FREE_DAYS

import datetime

# Create your models here.

class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    edition = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    price = models.PositiveIntegerField()
    late_fee = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.name


class IssuedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    returned = models.BooleanField(default=False)
    issue_date = models.DateField(default=now)
    # issue_date = models.DateField(auto_now_add=True, editable=True)

    def __str__(self):
        return self.user.first_name + ' issue ' + self.book.name


class SubmissionDetail(models.Model):
    late_submit = models.BooleanField(default=False)
    late_fee_amount = models.PositiveIntegerField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issued_book = models.ForeignKey(IssuedBook, on_delete=models.SET_NULL, null=True)
    return_date = models.DateField(default=now)
    # return_date = models.DateField(auto_now_add=True, editable=True)

    def __str__(self):
        return self.user.first_name
    
    def save(self, *args, **kwargs):
        current_date = datetime.date.today()
        issued_date = self.issued_book.issue_date

        between_days = current_date - issued_date
        between_days = between_days.days
        days_without_charge = BOOK_FREE_DAYS

        if between_days < days_without_charge:
            self.late_fee_amount = 0
            self.late_submit = False

        else:
            charges_day = between_days-days_without_charge
            late_fee = self.issued_book.book.late_fee
            self.late_fee_amount = charges_day * late_fee
            self.late_submit = True

        super(SubmissionDetail, self).save(*args, **kwargs)    
