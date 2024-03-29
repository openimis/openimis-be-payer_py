# Generated by Django 3.2.19 on 2023-12-12 09:33

import core.fields
import dirtyfields.dirtyfields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_auto_20230510_1347'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payer', '0003_set_managed_to_true'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalFunding',
            fields=[
                ('id', models.UUIDField(db_column='UUID', db_index=True, default=None, editable=False)),
                ('is_deleted', models.BooleanField(db_column='isDeleted', default=False)),
                ('json_ext', models.JSONField(blank=True, db_column='Json_ext', null=True)),
                ('date_created', core.fields.DateTimeField(db_column='DateCreated', null=True)),
                ('date_updated', core.fields.DateTimeField(db_column='DateUpdated', null=True)),
                ('version', models.IntegerField(default=1)),
                ('amount', models.DecimalField(blank=True, db_column='Amount', decimal_places=2, max_digits=18, null=True)),
                ('pay_date', models.DateField(blank=True, db_column='PaidDate', null=True)),
                ('status', models.CharField(choices=[('N', 'PENDING'), ('P', 'PAID'), ('A', 'AWAITING_FOR_RECONCILIATION'), ('R', 'RECONCILIATED')], db_column='Status', default='N', max_length=1)),
                ('receipt', models.CharField(db_column='Receipt', max_length=50)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('payer', models.ForeignKey(blank=True, db_column='PayerID', db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payer.payer')),
                ('product', models.ForeignKey(blank=True, db_column='ProdID', db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='product.product')),
                ('user_created', models.ForeignKey(blank=True, db_column='UserCreatedUUID', db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user_updated', models.ForeignKey(blank=True, db_column='UserUpdatedUUID', db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical funding',
                'verbose_name_plural': 'historical fundings',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Funding',
            fields=[
                ('id', models.UUIDField(db_column='UUID', default=None, editable=False, primary_key=True, serialize=False)),
                ('is_deleted', models.BooleanField(db_column='isDeleted', default=False)),
                ('json_ext', models.JSONField(blank=True, db_column='Json_ext', null=True)),
                ('date_created', core.fields.DateTimeField(db_column='DateCreated', null=True)),
                ('date_updated', core.fields.DateTimeField(db_column='DateUpdated', null=True)),
                ('version', models.IntegerField(default=1)),
                ('amount', models.DecimalField(blank=True, db_column='Amount', decimal_places=2, max_digits=18, null=True)),
                ('pay_date', models.DateField(blank=True, db_column='PaidDate', null=True)),
                ('status', models.CharField(choices=[('N', 'PENDING'), ('P', 'PAID'), ('A', 'AWAITING_FOR_RECONCILIATION'), ('R', 'RECONCILIATED')], db_column='Status', default='N', max_length=1)),
                ('receipt', models.CharField(db_column='Receipt', max_length=50)),
                ('payer', models.ForeignKey(blank=True, db_column='PayerID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='fundings', to='payer.payer')),
                ('product', models.ForeignKey(blank=True, db_column='ProdID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='fundings', to='product.product')),
                ('user_created', models.ForeignKey(db_column='UserCreatedUUID', on_delete=django.db.models.deletion.DO_NOTHING, related_name='funding_user_created', to=settings.AUTH_USER_MODEL)),
                ('user_updated', models.ForeignKey(db_column='UserUpdatedUUID', on_delete=django.db.models.deletion.DO_NOTHING, related_name='funding_user_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tblFunding',
                'managed': True,
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
    ]
