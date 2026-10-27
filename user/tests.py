import uuid

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile

PASSWORD = "KataSandiKuat123"


def buat_user(username="apel", **profile_data):
    """Bantu bikin user + profilnya (mirip yang dilakukan view register)."""
    user = User.objects.create_user(username=username, password=PASSWORD)
    profile = Profile.objects.create(user=user, **profile_data)
    return user, profile


class ProfileModelTests(TestCase):
    def test_id_profile_berupa_uuid(self):
        _, profile = buat_user()
        self.assertIsInstance(profile.id, uuid.UUID)

    def test_str_profile_adalah_username(self):
        _, profile = buat_user("jeruk")
        self.assertEqual(str(profile), "jeruk")


class RegisterTests(TestCase):
    def test_halaman_register_bisa_dibuka(self):
        response = self.client.get(reverse("user:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/register.html")

    def test_register_berhasil_membuat_user_dan_profile(self):
        response = self.client.post(reverse("user:register"), {
            "username": "baru",
            "password1": PASSWORD,
            "password2": PASSWORD,
        })
        self.assertRedirects(response, reverse("user:login"))
        user = User.objects.get(username="baru")
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_register_gagal_jika_password_tidak_sama(self):
        response = self.client.post(reverse("user:register"), {
            "username": "baru",
            "password1": PASSWORD,
            "password2": "BedaSekali456",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="baru").exists())

    def test_register_gagal_jika_username_sudah_dipakai(self):
        buat_user("apel")
        response = self.client.post(reverse("user:register"), {
            "username": "apel",
            "password1": PASSWORD,
            "password2": PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="apel").count(), 1)


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user, self.profile = buat_user("apel")

    def test_halaman_login_bisa_dibuka(self):
        response = self.client.get(reverse("user:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/login.html")

    def test_login_berhasil_diarahkan_ke_profil_sendiri(self):
        response = self.client.post(reverse("user:login"), {
            "username": "apel",
            "password": PASSWORD,
        }, follow=True)
        self.assertEqual(
            response.redirect_chain[-1][0],
            reverse("user:profile_detail", args=[self.profile.id]),
        )
        self.assertTrue(response.context["user"].is_authenticated)

    def test_login_gagal_jika_password_salah(self):
        response = self.client.post(reverse("user:login"), {
            "username": "apel",
            "password": "salah-total",
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_menghapus_sesi_dan_kembali_ke_login(self):
        self.client.login(username="apel", password=PASSWORD)
        response = self.client.get(reverse("user:logout"))
        self.assertRedirects(response, reverse("user:login"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ProfileDetailTests(TestCase):
    def setUp(self):
        self.user, self.profile = buat_user(
            "apel", bio="hai ini apel", phone_number="0812345678910", location="depok",
        )
        self.lain, _ = buat_user("jeruk")
        self.url = reverse("user:profile_detail", args=[self.profile.id])

    def test_profil_bisa_dilihat_tanpa_login_tapi_data_pribadi_tersembunyi(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "apel")
        self.assertContains(response, "hai ini apel")
        self.assertNotContains(response, "0812345678910")
        self.assertNotContains(response, "Ubah profil")

    def test_orang_lain_tidak_melihat_telepon_dan_tombol_ubah(self):
        self.client.login(username="jeruk", password=PASSWORD)
        response = self.client.get(self.url)
        self.assertFalse(response.context["is_owner"])
        self.assertNotContains(response, "0812345678910")
        self.assertNotContains(response, "Ubah profil")

    def test_pemilik_melihat_telepon_dan_tombol_ubah(self):
        self.client.login(username="apel", password=PASSWORD)
        response = self.client.get(self.url)
        self.assertTrue(response.context["is_owner"])
        self.assertContains(response, "0812345678910")
        self.assertContains(response, "Ubah profil")

    def test_profil_yang_tidak_ada_menghasilkan_404(self):
        url = reverse("user:profile_detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, 404)


class MyProfileTests(TestCase):
    def test_me_tanpa_login_dialihkan_ke_login(self):
        response = self.client.get(reverse("user:me"))
        self.assertRedirects(
            response, "/user/login/?next=/user/me/",
        )

    def test_me_mengarah_ke_profil_sendiri(self):
        _, profile = buat_user("apel")
        self.client.login(username="apel", password=PASSWORD)
        response = self.client.get(reverse("user:me"))
        self.assertRedirects(
            response, reverse("user:profile_detail", args=[profile.id]),
        )

    def test_me_membuat_profil_jika_belum_ada(self):
        admin = User.objects.create_superuser("admin", password=PASSWORD)
        self.assertFalse(Profile.objects.filter(user=admin).exists())
        self.client.login(username="admin", password=PASSWORD)
        self.client.get(reverse("user:me"))
        self.assertTrue(Profile.objects.filter(user=admin).exists())


class ProfileEditTests(TestCase):
    def setUp(self):
        self.user, self.profile = buat_user("apel", bio="lama")
        self.lain, self.profile_lain = buat_user("jeruk", bio="punya jeruk")
        self.url = reverse("user:profile_edit")

    def test_edit_tanpa_login_dialihkan_ke_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, "/user/login/?next=/user/me/edit/")

    def test_halaman_edit_bisa_dibuka_setelah_login(self):
        self.client.login(username="apel", password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/profile_edit.html")

    def test_edit_berhasil_menyimpan_perubahan(self):
        self.client.login(username="apel", password=PASSWORD)
        response = self.client.post(self.url, {
            "bio": "bio baru",
            "phone_number": "0811111111",
            "location": "bogor",
        })
        self.assertRedirects(
            response, reverse("user:profile_detail", args=[self.profile.id]),
        )
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "bio baru")
        self.assertEqual(self.profile.phone_number, "0811111111")
        self.assertEqual(self.profile.location, "bogor")

    def test_edit_hanya_mengubah_profil_sendiri(self):
        self.client.login(username="apel", password=PASSWORD)
        self.client.post(self.url, {
            "bio": "dibajak", "phone_number": "", "location": "",
        })
        self.profile_lain.refresh_from_db()
        self.assertEqual(self.profile_lain.bio, "punya jeruk")

    def test_edit_gagal_jika_nomor_telepon_terlalu_panjang(self):
        self.client.login(username="apel", password=PASSWORD)
        response = self.client.post(self.url, {
            "bio": "bio baru",
            "phone_number": "1" * 16,
            "location": "",
        })
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "lama")


class ShowUserTests(TestCase):
    def test_halaman_user_bisa_dibuka(self):
        response = self.client.get(reverse("user:show"))
        self.assertEqual(response.status_code, 200)