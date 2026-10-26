from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from item.models import Item


class LandingPageTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='pemilik', password='pass12345')

    def buat_barang(self, nama):
        return Item.objects.create(
            owner=self.owner, name=nama, description='Deskripsi barang',
            price_per_day=50000, location='Depok',
        )

    def test_landing_page_bisa_dibuka(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_landing_page_tanpa_barang(self):
        response = self.client.get(reverse('landing'))
        self.assertContains(response, 'Belum ada barang yang disewakan')

    def test_landing_page_menampilkan_barang_terbaru(self):
        self.buat_barang('Kamera DSLR')
        response = self.client.get(reverse('landing'))
        self.assertContains(response, 'Kamera DSLR')
        self.assertContains(response, 'Rp50000/hari')

    def test_landing_page_maksimal_enam_barang(self):
        for i in range(8):
            self.buat_barang(f'Barang {i}')
        response = self.client.get(reverse('landing'))
        self.assertEqual(len(response.context['latest_items']), 6)