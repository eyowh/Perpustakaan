# Generated by Django 5.2.1 on 2025-06-07 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peminjaman', '0009_peminjaman_kode_laporan'),
    ]

    operations = [
        migrations.AddField(
            model_name='peminjaman',
            name='status',
            field=models.CharField(choices=[('menunggu', 'Menunggu Persetujuan'), ('disetujui', 'Disetujui'), ('ditolak', 'Ditolak')], default='menunggu', max_length=20),
        ),
    ]
