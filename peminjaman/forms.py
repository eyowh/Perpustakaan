from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Buku, Peminjaman
from django.core.validators import RegexValidator
from django.utils import timezone

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        label="Nama Pengguna",
        help_text="Maksimal 150 karakter. Hanya huruf, angka dan simbol @/./+/-/_ yang diizinkan.",
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Hanya boleh berisi huruf, angka, dan karakter @ . + - _'
            )
        ],
        error_messages={
            'required': 'Nama pengguna wajib diisi.',
            'unique': 'Nama pengguna ini sudah digunakan.',
        }
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput)

class UpdateProfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nama_panjang', 'email', 'tgl_lahir', 'alamat', 'jenis_kelamin']
        widgets = {
            'tgl_lahir': forms.DateInput(attrs={'type': 'date'}),
        }

class TambahBukuForm(forms.ModelForm):
    class Meta:
        model = Buku
        fields = ['judul', 'penerbit', 'tahun_terbit', 'stok_buku', 'penulis', 'gambar']

class EditBukuForm(forms.ModelForm):
    class Meta:
        model = Buku
        fields = ['judul', 'penerbit', 'tahun_terbit', 'stok_buku', 'penulis', 'gambar']

class PeminjamanForm(forms.ModelForm):
    class Meta:
        model = Peminjaman
        fields = ['buku']

class PengembalianForm(forms.ModelForm):
    class Meta:
        model = Peminjaman
        fields = []  # Pengembalian hanya perlu submit; logika tanggal akan diatur di views

class DetailPeminjamanForm(forms.ModelForm):
    class Meta:
        model = Peminjaman
        fields = ['tanggal_pinjam', 'tanggal_kembali']
        widgets = {
            'tanggal_pinjam': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_kembali': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tanggal_pinjam = cleaned_data.get('tanggal_pinjam')
        tanggal_kembali = cleaned_data.get('tanggal_kembali')
        today = timezone.localdate()

        # Validasi: tanggal pinjam harus hari ini
        if tanggal_pinjam and tanggal_pinjam != today:
            self.add_error('tanggal_pinjam', "Tanggal pinjam harus sama dengan tanggal hari ini.")

        # Validasi: tanggal kembali harus setelah tanggal pinjam
        if tanggal_pinjam and tanggal_kembali and tanggal_kembali <= tanggal_pinjam:
            self.add_error('tanggal_kembali', "Tanggal kembali harus setelah tanggal pinjam.")

        return cleaned_data