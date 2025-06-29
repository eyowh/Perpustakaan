from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser
from random import randint
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta
import qrcode
import os
from django.conf import settings

# --------------------- USER ---------------------

class User(AbstractUser):
    nama_panjang = models.CharField(max_length=100, blank=True)
    tgl_lahir = models.DateField(null=True, blank=True)
    alamat = models.TextField(blank=True)

    JENIS_KELAMIN_CHOICES = (
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    )
    jenis_kelamin = models.CharField(max_length=1, choices=JENIS_KELAMIN_CHOICES, blank=True)
    kode_user = models.CharField(max_length=20, unique=True, blank=True, null=True)
    sudah_update_profil = models.BooleanField(default=False)

    def generate_kode_user(self):
        prefix = '2209'
        while True:
            angka = randint(1000, 9999)
            if self.jenis_kelamin == 'L' and angka % 2 == 0:
                kode = prefix + str(angka)
            elif self.jenis_kelamin == 'P' and angka % 2 != 0:
                kode = prefix + str(angka)
            else:
                continue
            if not User.objects.filter(kode_user=kode).exists():
                return kode

    def save(self, *args, **kwargs):
        if not self.kode_user and self.jenis_kelamin:
            self.kode_user = self.generate_kode_user()
        retry = 0
        while retry < 5:
            try:
                super().save(*args, **kwargs)
                return
            except IntegrityError:
                retry += 1
                self.kode_user = self.generate_kode_user()
        raise IntegrityError("Gagal menyimpan user karena kode_user tidak unik setelah beberapa percobaan.")

    def __str__(self):
        return self.username

# --------------------- BUKU ---------------------

class Buku(models.Model):
    judul = models.CharField(max_length=200)
    penerbit = models.CharField(max_length=100)
    tahun_terbit = models.IntegerField()
    stok_buku = models.PositiveIntegerField()
    penulis = models.CharField(max_length=100)
    gambar = models.ImageField(upload_to='gambar_buku/', null=True, blank=True)
    jumlah_dipinjam = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.judul

# --------------------- PEMINJAMAN ---------------------

class Peminjaman(models.Model):
    STATUS_CHOICES = (
        ('menunggu', 'Menunggu Persetujuan'),
        ('disetujui', 'Disetujui'),
        ('ditolak', 'Ditolak'),
        ('dikembalikan', 'Dikembalikan'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    buku = models.ForeignKey(Buku, on_delete=models.CASCADE)
    tanggal_pinjam = models.DateField(default=timezone.now)
    tanggal_kembali = models.DateField()
    tanggal_dikembalikan = models.DateField(null=True, blank=True)

    kode_laporan = models.CharField(max_length=30, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    qr_code_image = models.ImageField(upload_to='qrcodes/', null=True, blank=True)
    denda = models.IntegerField(default=0)
    denda_dibayar = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.kode_laporan} - {self.user.username} - {self.buku.judul}"

    def status_jatuh_tempo(self):
        if self.tanggal_dikembalikan:
            return "Dikembalikan"
        hari_ini = timezone.now().date()
        if self.tanggal_kembali < hari_ini:
            return "Terlambat"
        elif self.tanggal_kembali == hari_ini:
            return "Jatuh tempo hari ini"
        elif self.tanggal_kembali == hari_ini + timedelta(days=1):
            return "Besok jatuh tempo"
        else:
            return "Masih dipinjam"

    def generate_qr_code(self):
        # Tentukan konten QR berdasarkan status
        if self.status == 'menunggu':
            qr_data = f"PINJAM:{self.kode_laporan}"
        elif self.status == 'disetujui':
            qr_data = f"KEMBALI:{self.kode_laporan}"
        else:
            qr_data = f"{self.kode_laporan}"  # fallback aman

        # Simpan file PNG ke direktori media/qrcodes/
        folder = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, f'{self.kode_laporan}.png')

        # Buat QR dan simpan ke file
        img = qrcode.make(qr_data)
        img.save(file_path)

        # Simpan ke field ImageField
        self.qr_code_image = f'qrcodes/{self.kode_laporan}.png'

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_status = None

        # Cek status sebelumnya jika objek sudah ada
        if not is_new and self.pk:
            try:
                old = Peminjaman.objects.get(pk=self.pk)
                old_status = old.status
            except Peminjaman.DoesNotExist:
                pass

        # Buat kode laporan jika belum ada
        if not self.kode_laporan:
            prefix = "0307"
            id_user = f"{self.user.id:04d}"
            while True:
                nomor_unik = get_random_string(length=4, allowed_chars='0123456789')
                kode = f"{prefix}{id_user}{nomor_unik}"
                if not Peminjaman.objects.filter(kode_laporan=kode).exists():
                    self.kode_laporan = kode
                    break

        # Simpan dulu agar kode_laporan terisi dan ID ada
        super().save(*args, **kwargs)

        # Regenerate QR jika:
        # - Belum ada
        # - Atau status berubah (contoh: dari 'menunggu' ke 'disetujui')
        if (
            not self.qr_code_image or 
            (old_status and old_status != self.status)
        ):
            self.generate_qr_code()
            super().save(update_fields=['qr_code_image'])