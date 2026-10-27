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

    def test_halaman_edit_wajib_login(self):
        response = self.client.get(reverse('review:edit', args=[self.review.id]))
        self.assertEqual(response.status_code, 302)

    def test_halaman_ulasan_per_barang(self):
        response = self.client.get(reverse('review:item_reviews', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'?item={self.item.id}')

    def test_halaman_ulasan_barang_tidak_ada(self):
        response = self.client.get(reverse('review:item_reviews', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_form_ulasan_muncul_di_detail_order_selesai(self):
        self.login(self.penyewa)
        response = self.client.get(reverse('order:detail', args=[self.order_selesai.id]))
        self.assertContains(response, 'order-review-form')

    def test_form_ulasan_tidak_muncul_kalau_order_belum_selesai(self):
        self.login(self.penyewa)
        response = self.client.get(reverse('order:detail', args=[self.order_baru.id]))
        self.assertNotContains(response, 'order-review-form')
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

    # ---------- AJAX create ----------
    def test_create_ajax_berhasil(self):
        self.login(self.penyewa)
        url = reverse('review:create_ajax', args=[self.order_selesai.id])
        response = self.client.post(url, {'rating': 4, 'comment': 'Oke'})
        self.assertEqual(response.status_code, 201)
        review = Review.objects.get(pk=response.json()['id'])
        self.assertEqual(review.reviewer, self.penyewa)
        self.assertEqual(review.order, self.order_selesai)

    def test_create_ajax_tanpa_login_ditolak(self):
        url = reverse('review:create_ajax', args=[self.order_selesai.id])
        response = self.client.post(url, {'rating': 4})
        self.assertEqual(response.status_code, 401)

    def test_create_ajax_order_belum_selesai_ditolak(self):
        self.login(self.penyewa)
        url = reverse('review:create_ajax', args=[self.order_baru.id])
        response = self.client.post(url, {'rating': 4})
        self.assertEqual(response.status_code, 400)

    def test_create_ajax_bukan_penyewa_ditolak(self):
        self.login(self.pemilik)
        url = reverse('review:create_ajax', args=[self.order_selesai.id])
        response = self.client.post(url, {'rating': 4})
        self.assertEqual(response.status_code, 403)

    def test_create_ajax_order_sudah_diulas_ditolak(self):
        self.login(self.penyewa)
        url = reverse('review:create_ajax', args=[self.order_lama.id])
        response = self.client.post(url, {'rating': 4})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.objects.filter(order=self.order_lama).count(), 1)

    def test_create_ajax_rating_salah_ditolak(self):
        self.login(self.penyewa)
        url = reverse('review:create_ajax', args=[self.order_selesai.id])
        response = self.client.post(url, {'rating': 9})
        self.assertEqual(response.status_code, 400)

    # ---------- Edit & Delete ----------
    def test_edit_review_sendiri(self):
        self.login(self.penyewa)
        self.client.post(reverse('review:edit', args=[self.review.id]), {'rating': 2, 'comment': 'Diubah'})
        self.review.refresh_from_db()
        self.assertEqual(self.review.comment, 'Diubah')

    def test_tidak_bisa_edit_review_orang_lain(self):
        self.login(self.pemilik)
        response = self.client.get(reverse('review:edit', args=[self.review.id]))
        self.assertEqual(response.status_code, 404)

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