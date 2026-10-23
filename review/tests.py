from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from item.models import Item
from review.forms import ReviewForm
from review.models import Review

class ReviewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='mitsuri', password='pass12345')
        self.other = User.objects.create_user(username='obanai', password='pass12345')
        self.item = Item.objects.create(user=self.other, name='Kamera', description='Kamera DSLR', price_per_day=50000, stock=1)
        self.my_item = Item.objects.create(user=self.user, name='Tenda', description='Tenda 4 orang', price_per_day=30000, stock=1)
        self.review = Review.objects.create(reviewer=self.user, item=self.item, rating=5, comment='Bagus')
        self.other_review = Review.objects.create(reviewer=self.other, item=self.my_item, rating=3, comment='Lumayan')

    def test_str_review(self):
        self.assertEqual(str(self.review), 'mitsuri - 5*')

    def test_form_tolak_rating_di_luar_1_sampai_5(self):
        self.assertFalse(ReviewForm(data={'item': self.item.id, 'rating': 0}).is_valid())
        self.assertFalse(ReviewForm(data={'item': self.item.id, 'rating': 6}).is_valid())
        self.assertTrue(ReviewForm(data={'item': self.item.id, 'rating': 1}).is_valid())

    def test_form_wajib_pilih_barang(self):
        self.assertFalse(ReviewForm(data={'rating': 5}).is_valid())

    def test_tidak_bisa_review_barang_sendiri(self):
        self.assertFalse(ReviewForm(data={'rating': 5}).is_valid())

    def test_tidak_bisa_review_barang_sendiri(self):
        form = ReviewForm(data={'item': self.my_item.id, 'rating': 5}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('item', form.errors)

    def test_halaman_review_bisa_dibuka(self):
        response = self.client.get(reverse('review:show'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review/review_list.html')

    def test_halaman_create_wajib_login(self):
        response = self.client.get(reverse('review:create'))
        self.assertEqual(response.status_code, 302)

    def test_json_berisi_semua_review(self):
        self.client.login(username='mitsuri', password='pass12345')
        data = self.client.get(reverse('review:show_json')).json()
        self.assertEqual(len(data), 2)
        punya_saya = next(r for r in data if r['id'] == self.review.id)
        punya_orang = next(r for r in data if r['id'] == self.other_review.id)
        self.assertTrue(punya_saya['is_owner'])
        self.assertFalse(punya_orang['is_owner'])
        self.assertEqual(punya_saya['item'], 'Kamera')

    def test_json_bisa_difilter_per_barang(self):
        url = reverse('review:show_json') + f'?item={self.item.id}'
        data = self.client.get(url).json()
        self.assertEqual([r['id'] for r in data], [self.review.id])

    def test_create_ajax_berhasil(self):
        self.client.login(username='mitsuri', password='pass12345')
        response = self.client.post(reverse('review:create_ajax'), {'item': self.item.id, 'rating': 4, 'comment': 'Oke'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Review.objects.get(pk=response.json()['id']).reviewer, self.user)

    def test_create_ajax_tanpa_login_ditolak(self):
        response = self.client.post(reverse('review:create_ajax'), {'rating': 4})
        self.assertEqual(response.status_code, 401)

    def test_create_ajax_rating_salah_ditolak(self):
        self.client.login(username='mitsuri', password='pass12345')
        response = self.client.post(reverse('review:create_ajax'), {'item': self.item.id, 'rating': 9})
        self.assertEqual(response.status_code, 400)

    def test_edit_review_sendiri(self):
        self.client.login(username='mitsuri', password='pass12345')
        self.client.post(reverse('review:edit', args=[self.review.id]), {'item': self.item.id, 'rating': 2, 'comment': 'Diubah'})
        self.review.refresh_from_db()
        self.assertEqual(self.review.comment, 'Diubah')

    def test_tidak_bisa_edit_review_orang_lain(self):
        self.client.login(username='mitsuri', password='pass12345')
        response = self.client.get(reverse('review:edit', args=[self.other_review.id]))
        self.assertEqual(response.status_code, 404)

    def test_delete_ajax_review_sendiri(self):
        self.client.login(username='mitsuri', password='pass12345')
        response = self.client.post(reverse('review:delete_ajax', args=[self.review.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.filter(pk=self.review.id).exists())

    def test_tidak_bisa_delete_review_orang_lain(self):
        self.client.login(username='mitsuri', password='pass12345')
        response = self.client.post(reverse('review:delete_ajax', args=[self.other_review.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Review.objects.filter(pk=self.other_review.id).exists())

    def test_delete_lewat_get_ditolak(self):
        self.client.login(username='mitsuri', password='pass12345')
        response = self.client.get(reverse('review:delete', args=[self.review.id]))
        self.assertEqual(response.status_code, 405)