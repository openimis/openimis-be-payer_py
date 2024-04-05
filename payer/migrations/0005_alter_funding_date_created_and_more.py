# Generated by Django 4.2.9 on 2024-02-07 16:47

import core.fields
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payer', '0004_funding_historicalfunding'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funding',
            name='date_created',
            field=core.fields.DateTimeField(db_column='DateCreated', default=datetime.datetime.now, null=True),
        ),
        migrations.AlterField(
            model_name='funding',
            name='date_updated',
            field=core.fields.DateTimeField(db_column='DateUpdated', default=datetime.datetime.now, null=True),
        ),
        migrations.AlterField(
            model_name='funding',
            name='user_created',
            field=models.ForeignKey(db_column='UserCreatedUUID', on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_user_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='funding',
            name='user_updated',
            field=models.ForeignKey(db_column='UserUpdatedUUID', on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_user_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='historicalfunding',
            name='date_created',
            field=core.fields.DateTimeField(db_column='DateCreated', default=datetime.datetime.now, null=True),
        ),
        migrations.AlterField(
            model_name='historicalfunding',
            name='date_updated',
            field=core.fields.DateTimeField(db_column='DateUpdated', default=datetime.datetime.now, null=True),
        ),
    ]