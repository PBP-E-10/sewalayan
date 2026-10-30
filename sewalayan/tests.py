from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

class LandingPageTest(TestCase):
    def test_landing_page_bisa_dibuka(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_landing_page_punya_tombol_ke_katalog_dan_sewakan(self):
        response = self.client.get(reverse('landing'))
        self.assertContains(response, reverse('item:list'))
        self.assertContains(response, reverse('item:create'))

    def test_landing_page_tidak_menampilkan_daftar_barang(self):
        response = self.client.get(reverse('landing'))
        self.assertNotContains(response, 'Barang Terbaru')

class NavbarTest(TestCase):
    def test_navbar_tamu_ada_masuk_dan_daftar(self):
        response = self.client.get(reverse('landing'))
        self.assertContains(response, reverse('user:login'))
        self.assertContains(response, reverse('user:register'))
        self.assertNotContains(response, reverse('order:show'))

    def test_navbar_user_login_ada_pesanan_dan_keluar(self):
        User.objects.create_user(username='penyewa', password='pass12345')
        self.client.login(username='penyewa', password='pass12345')
        response = self.client.get(reverse('landing'))
        self.assertContains(response, reverse('order:show'))
        self.assertContains(response, reverse('user:logout'))
        self.assertContains(response, 'penyewa')

    def test_navbar_menandai_halaman_aktif(self):
        response = self.client.get(reverse('review:show'))
        self.assertContains(response, 'aria-current="page">Ulasan')

class LandingCategoryTest(TestCase):
    fixtures = ['categories']

    def test_landing_menampilkan_semua_kategori(self):
        response = self.client.get(reverse('landing'))
        self.assertContains(response, 'Kamera &amp; Fotografi')
        self.assertContains(response, 'Olahraga')
        self.assertContains(response, reverse('item:list') + '?category=2')

    def test_katalog_memilih_kategori_dari_url(self):
        response = self.client.get(reverse('item:list') + '?category=2')
        self.assertContains(response, '<option value="2" selected>')