# Generated by Django 4.2.10 on 2024-03-04 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_fix_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='collect',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='payment/images/', verbose_name='Обложка'),
        ),
    ]
