# Generated by Django 4.0.6 on 2024-10-30 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0031_category_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, default='static/images/blank_prodimg.jpg', null=True, upload_to='uploads/products/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/products/thumb/'),
        ),
    ]
