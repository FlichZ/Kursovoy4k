# Generated by Django 4.1 on 2023-11-17 20:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0007_alter_product_available_alter_review_author_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Имя тега")),
                ("slug", models.SlugField(unique=True)),
            ],
            options={
                "verbose_name": "Теги",
                "verbose_name_plural": "Теги",
                "ordering": ("name",),
            },
        ),
        migrations.AddField(
            model_name="product",
            name="tags",
            field=models.ManyToManyField(to="shop.tag", verbose_name="Тег"),
        ),
    ]
