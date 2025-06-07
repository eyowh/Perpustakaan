from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # User
    path('user/dashboard/', views.dashboard_user, name='dashboard_user'),
    path('user/update-profil/', views.update_profil, name='update_profil'),
    path('user/pinjam-buku/', views.pinjam_buku, name='pinjam_buku'),
    path('user/kembalikan-buku/<int:id>/', views.kembalikan_buku, name='kembalikan_buku'),
    path('user/buku-dipinjam/', views.buku_dipinjam_user, name='buku_dipinjam_user'),

    # Admin
    path('admin-panel/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('admin-panel/daftar-buku/', views.daftar_buku, name='daftar_buku'),
    path('admin-panel/tambah-buku/', views.tambah_buku, name='tambah_buku'),
    path('admin-panel/edit-buku/<int:id>/', views.edit_buku, name='edit_buku'),
    path('admin-panel/hapus-buku/<int:id>/', views.hapus_buku, name='hapus_buku'),
    path('admin-panel/laporan-peminjaman/', views.laporan_peminjaman, name='laporan_peminjaman'),
    path('admin-panel/biodata-user/', views.biodata_user, name='biodata_user'),
    
    path('export-excel/', views.export_peminjaman_excel, name='export_excel'),
    path('admin-panel/scan-pengembalian/', views.scan_pengembalian, name='scan_pengembalian'),
path('admin-panel/verifikasi/<str:kode>/', views.verifikasi_pengembalian, name='verifikasi_pengembalian'),
path('admin-panel/scan-peminjaman/', views.scan_peminjaman, name='scan_peminjaman'),
path('admin-panel/verifikasi-peminjaman/', views.verifikasi_peminjaman, name='verifikasi_peminjaman'),
]
