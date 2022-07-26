from time import sleep
from django.db import models
from django.contrib.auth.models import User

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
    issue_date = models.DateField(auto_created=True, auto_now_add=True)

    def __str__(self):
        return self.user.first_name + ' issue ' + self.book.name


class PaneltyDetail(models.Model):
    late_submit = models.BooleanField()
    late_fee_amount = models.PositiveIntegerField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issued_book = models.ForeignKey(IssuedBook, on_delete=models.SET_NULL, null=True)
    return_date = models.DateField(auto_created=True)

    def __str__(self):
        return self.user.first_name + ' with panelty ' + self.amount
    
    def save(self, *args, **kwargs):
        current_date = datetime.date.today()
        issued_date = self.issued_book.issue_date

        between_days = current_date - issued_date
        days_without_charge = 5

        if between_days < days_without_charge:
            self.late_fee_amount = 0
            self.late_submit = False

        else:
            charges_day = between_days-days_without_charge
            late_fee = self.issued_book.book.late_fee
            self.late_fee_amount = charges_day * late_fee
            self.late_submit = True

        super(PaneltyDetail, self).save(*args, **kwargs)    
