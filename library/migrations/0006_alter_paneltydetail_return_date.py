# Generated by Django 4.0.6 on 2022-07-27 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_paneltydetail_late_submit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paneltydetail',
            name='return_date',
            field=models.DateField(auto_created=True, auto_now_add=True),
        ),
    ]
