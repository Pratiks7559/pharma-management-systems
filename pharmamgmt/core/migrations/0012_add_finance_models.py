# Generated manually for finance models

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_add_performance_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMaster',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('payment_date', models.DateField(default=django.utils.timezone.now)),
                ('payment_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('bank', 'Bank Transfer'), ('cheque', 'Cheque'), ('card', 'Card'), ('upi', 'UPI'), ('other', 'Other')], default='cash', max_length=50)),
                ('payment_description', models.TextField(blank=True, null=True)),
                ('payment_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
                'db_table': 'payment_master',
            },
        ),
        migrations.CreateModel(
            name='ReceiptMaster',
            fields=[
                ('receipt_id', models.AutoField(primary_key=True, serialize=False)),
                ('receipt_date', models.DateField(default=django.utils.timezone.now)),
                ('receipt_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('receipt_method', models.CharField(choices=[('cash', 'Cash'), ('bank', 'Bank Transfer'), ('cheque', 'Cheque'), ('card', 'Card'), ('upi', 'UPI'), ('other', 'Other')], default='cash', max_length=50)),
                ('receipt_description', models.TextField(blank=True, null=True)),
                ('receipt_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Receipt',
                'verbose_name_plural': 'Receipts',
                'db_table': 'receipt_master',
            },
        ),
    ]