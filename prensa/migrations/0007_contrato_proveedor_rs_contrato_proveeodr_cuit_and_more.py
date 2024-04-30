# Generated by Django 4.2.10 on 2024-04-30 15:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('prensa', '0006_alter_contrato_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='contrato',
            name='proveedor_rs',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Proveedor Razón Social'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='proveeodr_cuit',
            field=models.BigIntegerField(blank=True, max_length=150, null=True, verbose_name='Programa'),
        ),
        migrations.AlterField(
            model_name='contrato',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
