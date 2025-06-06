from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser
from random import randint
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta

# Extend default User model
class User(AbstractUser):
    nama_panjang = models.CharField(max_length=100, blank=True)
    tgl_lahir = models.DateField(null=True, blank=True)
    alamat = models.TextField(blank=True)

    JENIS_KELAMIN_CHOICES = (
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    )
    jenis_kelamin = models.CharField(max_length=1, choices=JENIS_KELAMIN_CHOICES, blank=True)
    
    # Diubah: null=True supaya tidak error saat register
    kode_user = models.CharField(max_length=20, unique=True, blank=True, null=True)

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

            # Pastikan unik
            if not User.objects.filter(kode_user=kode).exists():
                return kode

    def save(self, *args, **kwargs):
        # Hanya generate kalau belum punya kode_user dan jenis_kelamin diisi
        if not self.kode_user and self.jenis_kelamin:
            self.kode_user = self.generate_kode_user()

        # Tangani potensi konflik kode_user meskipun sudah dicek
        retry = 0
        while retry < 5:
            try:
                super().save(*args, **kwargs)
                return
            except IntegrityError:
                # kode_user bentrok? generate baru lalu coba simpan lagi
                retry += 1
                self.kode_user = self.generate_kode_user()

        raise IntegrityError("Gagal menyimpan user karena kode_user tidak unik setelah beberapa percobaan.")

    def __str__(self):
        return self.username

class Buku(models.Model):
    judul = models.CharField(max_length=200)
    penerbit = models.CharField(max_length=100)
    tahun_terbit = models.IntegerField()
    stok_buku = models.PositiveIntegerField()
    penulis = models.CharField(max_length=100)
    gambar = models.ImageField(upload_to='gambar_buku/', null=True, blank=True)
    jumlah_dipinjam = models.PositiveIntegerField(default=0)  # Untuk melacak yang sering dipinjam

    def __str__(self):
        return self.judul

class Peminjaman(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    buku = models.ForeignKey(Buku, on_delete=models.CASCADE)
    tanggal_pinjam = models.DateField(default=timezone.now)
    tanggal_kembali = models.DateField()  # Rencana kembali
    tanggal_dikembalikan = models.DateField(null=True, blank=True)  # Realisasi

    kode_laporan = models.CharField(max_length=30, unique=True, blank=True)

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

    def save(self, *args, **kwargs):
        if not self.kode_laporan:
            prefix = "0307"
            id_user = f"{self.user.id:04d}"  # padding id user
            while True:
                nomor_unik = get_random_string(length=4, allowed_chars='0123456789')
                kode = f"{prefix}{id_user}{nomor_unik}"
                if not Peminjaman.objects.filter(kode_laporan=kode).exists():
                    self.kode_laporan = kode
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.kode_laporan} - {self.user.username} - {self.buku.judul}"

