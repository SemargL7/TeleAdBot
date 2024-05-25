# Generated by Django 4.2.13 on 2024-05-24 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlockChain',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('callback_url', models.TextField()),
                ('callback_x_key', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('order_id', models.CharField(max_length=200, unique=True)),
                ('type', models.CharField(choices=[('deposit', 'Deposit'), ('withdrawal', 'Withdrawal')], max_length=50)),
                ('status', models.CharField(choices=[('unapproved', 'Unapproved'), ('pending', 'Pending'), ('completed', 'Completed'), ('rejected', 'Rejected')], default='unapproved', max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.merchant')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('decimals', models.IntegerField(default=0)),
                ('blockchain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.blockchain')),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100, unique=True)),
                ('private_key', models.CharField(max_length=100)),
                ('is_hotspot', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('blockchain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.blockchain')),
            ],
        ),
        migrations.CreateModel(
            name='WithdrawalPaymentOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to_address', models.CharField(max_length=200)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.order')),
                ('wallet', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wallet.wallet')),
            ],
        ),
        migrations.CreateModel(
            name='WalletBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.BigIntegerField(default=0)),
                ('token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.token')),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.wallet')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('hash_transaction', models.CharField(max_length=100)),
                ('amount', models.BigIntegerField()),
                ('type', models.CharField(choices=[('deposit', 'Deposit'), ('withdrawal', 'Withdrawal'), ('transfer_in', 'Transfer_in'), ('transfer_out', 'Transfer_out')], max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('rejected', 'Rejected')], max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wallet.order')),
                ('to_wallet', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='incoming_transactions', to='wallet.wallet')),
                ('token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.token')),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='wallet.wallet')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='token',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.token'),
        ),
        migrations.CreateModel(
            name='MerchantWallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.BigIntegerField(default=0)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.merchant')),
                ('token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.token')),
            ],
        ),
        migrations.CreateModel(
            name='MerchantApiKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_key', models.TextField()),
                ('private_key', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('can_create_deposit_order', models.BooleanField(default=False)),
                ('can_create_withdrawal_order', models.BooleanField(default=False)),
                ('can_check_balance', models.BooleanField(default=False)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.merchant')),
            ],
        ),
        migrations.CreateModel(
            name='Liquidity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proc_token_min_value', models.BigIntegerField()),
                ('required_token_min_value', models.BigIntegerField()),
                ('proc_token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proc_token_liquidity', to='wallet.token')),
                ('required_token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='required_token_liquidity', to='wallet.token')),
            ],
        ),
        migrations.CreateModel(
            name='DepositPaymentOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.order')),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.wallet')),
            ],
        ),
    ]