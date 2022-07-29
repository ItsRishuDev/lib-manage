from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class MemberDetails(models.Model):
    Student = 'Student'
    Faculty = 'Faculty'
    MEMBER_CHOICES = [
        (Student, 'Student'),
        (Faculty, 'Faculty'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.PositiveBigIntegerField()
    bookLimit = models.PositiveIntegerField(null=True, blank=True)
    issuedBook = models.PositiveIntegerField(default=0)
    member_type = models.CharField(choices=MEMBER_CHOICES, max_length=7)

    def save(self, *args, **kwargs):
        if self.issuedBook is None:
            if self.member_type == "Faculty":
                self.bookLimit = 4
            else:
                self.bookLimit = 2

        super(MemberDetails, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.first_name          

