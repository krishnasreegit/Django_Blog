# Generated by Django 5.0.3 on 2025-03-24 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='description',
            field=models.CharField(blank=True, help_text='Enter a brief description of your blog post.', max_length=500, null=True),
        ),
    ]
