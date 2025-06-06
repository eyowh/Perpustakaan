# Generated by Django 5.2.1 on 2025-05-30 10:17

import datetime
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peminjaman', '0007_peminjaman_tanggal_dikembalikan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='peminjaman',
            name='tanggal_dikembalikan',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='peminjaman',
            name='tanggal_kembali',
            field=models.DateField(default=datetime.date(2025, 5, 30)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='peminjaman',
            name='tanggal_pinjam',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
