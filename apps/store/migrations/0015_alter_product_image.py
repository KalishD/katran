# Generated by Django 4.0.6 on 2022-07-18 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, default='static/images/blank_prodimg.jpg', null=True, upload_to='media/uploads/'),
        ),
    ]
