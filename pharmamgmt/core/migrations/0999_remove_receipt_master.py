from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_alter_receiptmaster_receipt_date'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ReceiptMaster',
        ),
    ]