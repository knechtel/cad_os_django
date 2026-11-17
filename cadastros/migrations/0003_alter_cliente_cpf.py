from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cadastros", "0002_aparelho_created_at_aparelho_delivered_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cliente",
            name="cpf",
            field=models.CharField(blank=True, max_length=14, null=True, verbose_name="CPF"),
        ),
    ]
