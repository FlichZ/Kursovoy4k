# Generated by Django 4.1 on 2022-08-26 07:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0002_alter_product_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(
                default=True, upload_to="", verbose_name="Изображение"
            ),
        ),
    ]
