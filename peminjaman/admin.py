from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Buku, Peminjaman

class UserAdmin(BaseUserAdmin):
    # Menampilkan field tambahan di admin user
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('nama_panjang', 'tgl_lahir', 'alamat')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('nama_panjang', 'tgl_lahir', 'alamat')}),
    )
    list_display = ['username', 'nama_panjang', 'email', 'is_staff', 'is_superuser']

class BukuAdmin(admin.ModelAdmin):
    list_display = ['judul', 'penulis', 'penerbit', 'tahun_terbit', 'stok_buku', 'jumlah_dipinjam']
    search_fields = ['judul', 'penulis']
    list_filter = ['penerbit', 'tahun_terbit']

class PeminjamanAdmin(admin.ModelAdmin):
    list_display = ['user', 'buku', 'tanggal_pinjam', 'tanggal_kembali']
    search_fields = ['user__username', 'buku__judul']
    list_filter = ['tanggal_pinjam', 'tanggal_kembali']

admin.site.register(User, UserAdmin)
admin.site.register(Buku, BukuAdmin)
admin.site.register(Peminjaman, PeminjamanAdmin)
