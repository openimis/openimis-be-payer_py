# Generated by Django 3.2.18 on 2023-05-12 14:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payer', '0001_initial'),
        ('location', '0013_auto_20230317_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='payer',
            name='location',
            field=models.ForeignKey(blank=True, db_column='LocationId', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='location.location'),
        ),
    ]
