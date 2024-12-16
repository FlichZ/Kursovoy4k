# Generated by Django 5.1 on 2024-12-02 22:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0006_alter_order_created_alter_order_updated"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Дата создания"),
        ),
        migrations.AlterField(
            model_name="order",
            name="updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
        ),
    ]