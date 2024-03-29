# Generated by Django 4.0.6 on 2022-07-25 08:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0021_brand_image_brand_thumbnail'),
    ]

    operations = [
        migrations.CreateModel(
            name='VariableItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('dimention', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variables', to='store.product')),
                ('varitem', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='variables', to='store.variableitem')),
            ],
        ),
    ]
