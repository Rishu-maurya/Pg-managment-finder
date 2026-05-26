# Generated migration for PhonePe UPI integration
# Removes Razorpay fields and adds PhonePe fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pgs', '0007_payment_rating_review'),
    ]

    operations = [
        # Remove Razorpay fields
        migrations.RemoveField(
            model_name='payment',
            name='razorpay_order_id',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='razorpay_payment_id',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='razorpay_signature',
        ),

        # Add PhonePe fields
        migrations.AddField(
            model_name='payment',
            name='phonepe_order_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='phonepe_transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='phonepe_response_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),

        # Update payment_method choices and default
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(
                choices=[('upi', 'UPI'), ('card', 'Card'), ('other', 'Other')],
                default='upi',
                max_length=20
            ),
        ),

        # Data migration: Update existing Payment records to use 'upi' method
        migrations.RunPython(
            lambda apps, schema_editor: apps.get_model('pgs', 'Payment').objects.filter(payment_method='razorpay').update(payment_method='upi'),
            reverse_code=migrations.RunPython.noop,
        ),
    ]
