# Generated migration to remove PhonePe fields and simplify Payment model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pgs', '0008_remove_razorpay_add_phonepe'),
    ]

    operations = [
        # Remove PhonePe-specific fields
        migrations.RemoveField(
            model_name='payment',
            name='phonepe_order_id',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='phonepe_transaction_id',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='phonepe_response_code',
        ),

        # Update payment_status field choices
        migrations.AlterField(
            model_name='payment',
            name='payment_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Payment Pending'),
                    ('pending_verification', 'Pending Verification'),
                    ('completed', 'Payment Completed'),
                    ('failed', 'Payment Failed'),
                    ('cancelled', 'Cancelled')
                ],
                default='pending',
                max_length=20
            ),
        ),

        # Update transaction_id field to remove unique constraint
        migrations.AlterField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
