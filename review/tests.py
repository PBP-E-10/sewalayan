from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from item.models import Item
from order.models import Order
from review.forms import ReviewForm
from review.models import Review


class ReviewTest(TestCase):
    def setUp(self):
        self.penyewa = User.objects.create_user(username='penyewa', password='pass12345')
        self.pemilik = User.objects.create_user(username='pemilik', password='pass12345')

        self.item = Item.objects.create(
            owner=self.pemilik, name='Kamera', description='Kamera DSLR',
            price_per_day=50000, location='Depok',
        )

        self.order_selesai = self.buat_order(status='finished')
        self.order_baru = self.buat_order(status='paid')
        self.order_lama = self.buat_order(status='finished')

        self.review = Review.objects.create(
            reviewer=self.penyewa, order=self.order_lama, rating=5, comment='Bagus',
        )

    def buat_order(self, status, buyer=None):
        return Order.objects.create(
            item=self.item, buyer=buyer or self.penyewa, status=status,
            purchase_price=50000, returned_at=timezone.now() + timedelta(days=1),
        )

    def login(self, user):
        self.client.login(username=user.username, password='pass12345')

    # ---------- Model & Form ----------
    def test_str_review(self):
        self.assertEqual(str(self.review), 'penyewa - 5*')

    def test_form_tolak_rating_di_luar_1_sampai_5(self):
        self.assertFalse(ReviewForm(data={'rating': 0}).is_valid())
        self.assertFalse(ReviewForm(data={'rating': 6}).is_valid())
        self.assertTrue(ReviewForm(data={'rating': 1}).is_valid())

    def test_review_terhubung_ke_order(self):
        self.assertEqual(self.order_lama.review, self.review)
        self.assertEqual(self.review.order.item, self.item)

    # ---------- Halaman ----------
    def test_halaman_review_bisa_dibuka(self):
        response = self.client.get(reverse('review:show'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review/review_list.html')

    def test_halaman_ulasan_wajib_login(self):
        response = self.client.get(reverse('review:order_review', args=[self.order_selesai.id]))
        self.assertEqual(response.status_code, 302)

    def test_halaman_ulasan_per_barang(self):
        response = self.client.get(reverse('review:item_reviews', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'?item={self.item.id}')

    def test_halaman_ulasan_barang_tidak_ada(self):
        response = self.client.get(reverse('review:item_reviews', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_tombol_tulis_ulasan_muncul_kalau_order_selesai(self):
        self.login(self.penyewa)
        response = self.client.get(reverse('order:detail', args=[self.order_selesai.id]))
        self.assertContains(response, 'Tulis Ulasan')

    def test_tombol_tulis_ulasan_tidak_muncul_kalau_belum_selesai(self):
        self.login(self.penyewa)
        response = self.client.get(reverse('order:detail', args=[self.order_baru.id]))
        self.assertNotContains(response, 'Tulis Ulasan')
        self.assertContains(response, 'setelah sewa selesai')

    # ---------- JSON ----------
    def test_json_berisi_review_dan_nama_barang(self):
        self.login(self.penyewa)
        data = self.client.get(reverse('review:show_json')).json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['item'], 'Kamera')
        self.assertTrue(data[0]['is_owner'])

    def test_json_bisa_difilter_per_barang(self):
        url = reverse('review:show_json') + f'?item={self.item.id}'
        self.assertEqual(len(self.client.get(url).json()), 1)
        url = reverse('review:show_json') + '?item=9999'
        self.assertEqual(len(self.client.get(url).json()), 0)

    # ---------- Tulis & edit (satu halaman) ----------
    def test_tulis_ulasan_berhasil(self):
        self.login(self.penyewa)
        url = reverse('review:order_review', args=[self.order_selesai.id])
        response = self.client.post(url, {'rating': 4, 'comment': 'Oke'})
        self.assertRedirects(response, reverse('order:detail', args=[self.order_selesai.id]))
        review = Review.objects.get(order=self.order_selesai)
        self.assertEqual(review.reviewer, self.penyewa)
        self.assertEqual(review.rating, 4)

    def test_halaman_sama_jadi_mode_edit_kalau_sudah_diulas(self):
        self.login(self.penyewa)
        url = reverse('review:order_review', args=[self.order_lama.id])
        response = self.client.get(url)
        self.assertContains(response, 'Edit Ulasan')
        self.assertContains(response, 'Bagus')

        self.client.post(url, {'rating': 2, 'comment': 'Diubah'})
        self.review.refresh_from_db()
        self.assertEqual(self.review.comment, 'Diubah')
        self.assertEqual(Review.objects.filter(order=self.order_lama).count(), 1)

    def test_order_belum_selesai_tidak_bisa_diulas(self):
        self.login(self.penyewa)
        url = reverse('review:order_review', args=[self.order_baru.id])
        response = self.client.post(url, {'rating': 4})
        self.assertRedirects(response, reverse('order:detail', args=[self.order_baru.id]))
        self.assertFalse(Review.objects.filter(order=self.order_baru).exists())

    def test_bukan_penyewa_tidak_bisa_mengulas(self):
        self.login(self.pemilik)
        url = reverse('review:order_review', args=[self.order_selesai.id])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.get(reverse('review:order_review', args=[self.order_lama.id])).status_code, 404)

    def test_rating_salah_ditolak(self):
        self.login(self.penyewa)
        url = reverse('review:order_review', args=[self.order_selesai.id])
        response = self.client.post(url, {'rating': 9})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.filter(order=self.order_selesai).exists())

    # ---------- Delete ----------

    def test_delete_ajax_review_sendiri(self):
        self.login(self.penyewa)
        response = self.client.post(reverse('review:delete_ajax', args=[self.review.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.filter(pk=self.review.id).exists())

    def test_tidak_bisa_delete_review_orang_lain(self):
        self.login(self.pemilik)
        response = self.client.post(reverse('review:delete_ajax', args=[self.review.id]))
        self.assertEqual(response.status_code, 404)

    def test_delete_lewat_get_ditolak(self):
        self.login(self.penyewa)
        response = self.client.get(reverse('review:delete_ajax', args=[self.review.id]))
        self.assertEqual(response.status_code, 405)