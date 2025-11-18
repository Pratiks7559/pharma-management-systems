from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_challanseries_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerchallan',
            name='challan_total',
            field=models.FloatField(default=0.0),
        ),
    ]
