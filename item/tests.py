from decimal import Decimal
from unittest.mock import MagicMock, patch

import requests
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from item.grading import NOT_ELIGIBLE_GRADE, calculate_condition_grade, is_eligible
from item.models import Category, Item
from item.views import geocode_address

AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}


class ItemTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create(username="budi")
        self.other_user = User.objects.create(username="sari")
        self.category = Category.objects.create(name="Elektronik", slug="elektronik")
        self.item = Item.objects.create(
            owner=self.owner,
            category=self.category,
            name="Kamera Mirrorless",
            description="Kamera dengan lensa kit",
            price_per_day=Decimal("150000"),
            location="Depok",
            condition_grade="Grade A — Seperti Baru",
        )

    def item_data(self, **overrides):
        data = {
            "name": "Speaker Bluetooth",
            "description": "Speaker portabel, suara jernih",
            "price_per_day": "50000",
            "functional_score": 4,
            "physical_score": 4,
            "safety_score": 4,
            "completeness_score": 4,
            "hygiene_score": 4,
            "location": "Depok",
            "is_available": "on",
        }
        data.update(overrides)
        return data

    def json_names(self, **params):
        response = self.client.get(reverse("item:get_json"), params)
        self.assertEqual(response.status_code, 200)
        return [row["fields"]["name"] for row in response.json()]

    # Model 

    def test_item_model(self):
        self.assertEqual(str(self.item), "Kamera Mirrorless")
        self.assertEqual(self.item.owner, self.owner)
        self.assertEqual(self.item.functional_score, 4)
        self.assertTrue(self.item.is_available)

    def test_category_model(self):
        self.assertEqual(str(self.category), "Elektronik")

    def test_item_is_deleted_with_its_owner(self):
        self.owner.delete()

        self.assertEqual(Item.objects.count(), 0)

    def test_model_clean_rejects_not_eligible_item(self):
        item = Item(
            owner=self.owner, name="Rusak", description="Tidak aman",
            price_per_day=1000, location="Depok", safety_score=1,
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_model_clean_accepts_eligible_item(self):
        item = Item(
            owner=self.owner, name="Bagus", description="Aman",
            price_per_day=1000, location="Depok",
        )

        item.full_clean()

    # Grading 

    def test_condition_grade_rules(self):
        rules = [
            ({}, "Grade A — Seperti Baru"),
            ({"physical_score": 3, "completeness_score": 3}, "Grade B — Sangat Baik"),
            ({"physical_score": 2}, "Grade C — Baik/Layak Pakai"),
            ({"functional_score": 3}, "Grade C — Baik/Layak Pakai"),
            ({"functional_score": 2}, "Grade D — Cukup"),
        ]
        for scores, expected in rules:
            with self.subTest(scores=scores):
                item = Item(**scores)
                self.assertEqual(calculate_condition_grade(item), expected)

    def test_item_is_not_eligible(self):
        for scores in [{"safety_score": 2}, {"functional_score": 1}, {"hygiene_score": 1}]:
            with self.subTest(scores=scores):
                item = Item(**scores)
                self.assertEqual(calculate_condition_grade(item), NOT_ELIGIBLE_GRADE)
                self.assertFalse(is_eligible(item))

    def test_knockout_rule_beats_grade_d(self):
        item = Item(functional_score=2, safety_score=2)

        self.assertEqual(calculate_condition_grade(item), NOT_ELIGIBLE_GRADE)

    # Katalog 

    def test_item_list_page_is_accessible(self):
        response = self.client.get(reverse("item:list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "item/item_list.html")
        self.assertContains(response, self.category.name)
        self.assertNotContains(response, self.item.name)
        self.assertContains(response, reverse("item:get_json"))

    def test_create_button_only_for_logged_in_user(self):
        create_url = reverse("item:create")
        self.assertNotContains(self.client.get(reverse("item:list")), create_url)

        self.client.force_login(self.owner)
        self.assertContains(self.client.get(reverse("item:list")), create_url)

    # API json

    def test_get_items_json(self):
        response = self.client.get(reverse("item:get_json"))
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["pk"], str(self.item.pk))
        self.assertEqual(data[0]["fields"]["name"], "Kamera Mirrorless")
        self.assertEqual(data[0]["fields"]["price_per_day"], "150000.00")
        self.assertEqual(data[0]["fields"]["category_name"], "Elektronik")
        self.assertEqual(data[0]["fields"]["image"], "")

    def test_get_items_json_search(self):
        self.assertEqual(self.json_names(q="kamera"), ["Kamera Mirrorless"])
        self.assertEqual(self.json_names(q="LENSA"), ["Kamera Mirrorless"])
        self.assertEqual(self.json_names(q="tidak-ada"), [])

    def test_get_items_json_filters(self):
        Item.objects.create(
            owner=self.owner, name="Tenda Dome", description="Muat empat orang",
            price_per_day=Decimal("50000"), location="Bandung",
            condition_grade="Grade C — Baik/Layak Pakai",
        )
        filters = [
            ({"category": self.category.pk}, ["Kamera Mirrorless"]),
            ({"grade": "Grade C"}, ["Tenda Dome"]),
            ({"location": "bandung"}, ["Tenda Dome"]),
            ({"min_price": "100000"}, ["Kamera Mirrorless"]),
            ({"max_price": "100000"}, ["Tenda Dome"]),
            ({"min_price": "10000", "max_price": "60000"}, ["Tenda Dome"]),
        ]
        for params, expected in filters:
            with self.subTest(params=params):
                self.assertEqual(self.json_names(**params), expected)

    def test_get_items_json_ignores_invalid_filters(self):
        names = self.json_names(category="abc", min_price="abc", max_price="xyz")

        self.assertEqual(names, ["Kamera Mirrorless"])

    def test_get_items_json_hides_not_eligible_items(self):
        Item.objects.create(
            owner=self.owner, name="Barang Lama", description="Data lama",
            price_per_day=Decimal("1000"), location="Depok",
            condition_grade=NOT_ELIGIBLE_GRADE,
        )

        self.assertEqual(self.json_names(), ["Kamera Mirrorless"])

    def test_get_items_json_only_accepts_get(self):
        response = self.client.post(reverse("item:get_json"))

        self.assertEqual(response.status_code, 405)

    def test_get_items_json_ignores_special_decimal_values(self):
        for value in ["NaN", "sNaN", "Infinity", "-Infinity"]:
            with self.subTest(value=value):
                names = self.json_names(min_price=value, max_price=value)
                self.assertEqual(names, ["Kamera Mirrorless"])

    def test_get_items_json_ignores_non_ascii_category(self):
        self.assertEqual(self.json_names(category="²"), ["Kamera Mirrorless"])

    def test_get_items_json_with_very_long_keyword(self):
        self.assertEqual(self.json_names(q="a" * 100000), [])

    # Detail

    def test_item_detail_page(self):
        response = self.client.get(reverse("item:detail", args=[self.item.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "item/item_detail.html")
        self.assertContains(response, self.item.name)
        self.assertContains(response, "budi")
        self.assertContains(response, "● Tersedia")

    def test_nonexistent_item_returns_404(self):
        response = self.client.get(reverse("item:detail", args=[9999]))

        self.assertEqual(response.status_code, 404)

    def test_unavailable_item_label(self):
        self.item.is_available = False
        self.item.save()
        response = self.client.get(reverse("item:detail", args=[self.item.pk]))

        self.assertContains(response, "Tidak Tersedia")
        self.assertContains(response, "Sedang Disewa")

    def test_map_only_shown_with_coordinates(self):
        url = reverse("item:detail", args=[self.item.pk])
        self.assertContains(self.client.get(url), "Koordinat peta tidak tersedia")

        self.item.latitude, self.item.longitude = -6.4, 106.8
        self.item.save()
        self.assertContains(self.client.get(url), 'id="map"')

    def test_edit_and_delete_buttons_only_for_owner(self):
        detail_url = reverse("item:detail", args=[self.item.pk])
        update_url = reverse("item:update", args=[self.item.pk])
        delete_url = reverse("item:delete", args=[self.item.pk])

        self.client.force_login(self.other_user)
        response = self.client.get(detail_url)
        self.assertNotContains(response, update_url)
        self.assertNotContains(response, delete_url)

        self.client.force_login(self.owner)
        response = self.client.get(detail_url)
        self.assertContains(response, update_url)
        self.assertContains(response, delete_url)

    # -------------------------------------------------------------- create ---

    def test_create_requires_login(self):
        create_url = reverse("item:create")
        response = self.client.get(create_url)

        self.assertRedirects(
            response, f"{reverse('user:login')}?next={create_url}",
            fetch_redirect_response=False,
        )

    def test_create_page_for_logged_in_user(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("item:create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "item/item_form.html")

    @patch("item.views.geocode_address", return_value=(-6.4, 106.8))
    def test_create_item_success(self, mock_geocode):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("item:create"), self.item_data())
        item = Item.objects.get(name="Speaker Bluetooth")

        self.assertRedirects(response, reverse("item:list"), fetch_redirect_response=False)
        self.assertEqual(item.owner, self.owner)
        self.assertEqual(item.condition_grade, "Grade A — Seperti Baru")
        self.assertEqual((item.latitude, item.longitude), (-6.4, 106.8))
        mock_geocode.assert_called_once_with("Depok")

    @patch("item.views.geocode_address", return_value=(None, None))
    def test_create_item_ignores_grade_and_owner_from_client(self, mock_geocode):
        self.client.force_login(self.owner)
        self.client.post(reverse("item:create"), self.item_data(
            physical_score=3, completeness_score=3,
            condition_grade="Grade A — Seperti Baru", owner=self.other_user.pk,
        ))
        item = Item.objects.get(name="Speaker Bluetooth")

        self.assertEqual(item.condition_grade, "Grade B — Sangat Baik")
        self.assertEqual(item.owner, self.owner)

    @patch("item.views.geocode_address", return_value=(None, None))
    def test_create_item_with_zero_price(self, mock_geocode):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("item:create"), self.item_data(price_per_day="0"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Harga sewa harus lebih dari 0.")
        self.assertEqual(Item.objects.count(), 1)

    @patch("item.views.geocode_address", return_value=(None, None))
    def test_create_not_eligible_item_is_rejected(self, mock_geocode):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("item:create"), self.item_data(safety_score=2))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tidak layak disewakan")
        self.assertEqual(Item.objects.count(), 1)
        mock_geocode.assert_not_called()

    @patch("item.views.geocode_address", return_value=(None, None))
    def test_create_item_ajax(self, mock_geocode):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("item:create"), self.item_data(), **AJAX)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertIn("Grade A", response.json()["message"])
        self.assertEqual(Item.objects.count(), 2)

    @patch("item.views.geocode_address", return_value=(None, None))
    def test_create_item_ajax_invalid(self, mock_geocode):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("item:create"), self.item_data(price_per_day="0"), **AJAX,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertIn("price_per_day", response.json()["errors"])
        self.assertEqual(Item.objects.count(), 1)

    # Update 

    def test_update_requires_login(self):
        update_url = reverse("item:update", args=[self.item.pk])
        response = self.client.get(update_url)

        self.assertRedirects(
            response, f"{reverse('user:login')}?next={update_url}",
            fetch_redirect_response=False,
        )

    def test_update_page_for_owner(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("item:update", args=[self.item.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Barang")
        self.assertContains(response, self.item.name)

    @patch("item.views.geocode_address", return_value=(-7.0, 110.4))
    def test_update_item_by_owner(self, mock_geocode):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("item:update", args=[self.item.pk]),
            self.item_data(name="Kamera Baru", location="Semarang", functional_score=3),
        )
        self.item.refresh_from_db()

        self.assertRedirects(response, reverse("item:detail", args=[self.item.pk]))
        self.assertEqual(self.item.name, "Kamera Baru")
        self.assertEqual(self.item.condition_grade, "Grade C — Baik/Layak Pakai")
        self.assertEqual((self.item.latitude, self.item.longitude), (-7.0, 110.4))
        mock_geocode.assert_called_once_with("Semarang")

    @patch("item.views.geocode_address", return_value=(-7.0, 110.4))
    def test_update_does_not_geocode_when_location_unchanged(self, mock_geocode):
        self.client.force_login(self.owner)
        self.client.post(
            reverse("item:update", args=[self.item.pk]),
            self.item_data(name="Kamera Baru", location="Depok"),
        )

        mock_geocode.assert_not_called()

    @patch("item.views.geocode_address", return_value=(None, None))
    def test_update_item_by_other_user(self, mock_geocode):
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse("item:update", args=[self.item.pk]), self.item_data(name="Diretas"),
        )
        self.item.refresh_from_db()

        self.assertRedirects(response, reverse("item:detail", args=[self.item.pk]))
        self.assertEqual(self.item.name, "Kamera Mirrorless")

    @patch("item.views.geocode_address", return_value=(None, None))
    def test_update_not_eligible_item_is_rejected(self, mock_geocode):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("item:update", args=[self.item.pk]),
            self.item_data(name="Rusak", safety_score=1),
        )
        self.item.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tidak layak disewakan")
        self.assertEqual(self.item.name, "Kamera Mirrorless")

    # Delete 

    def test_delete_requires_login(self):
        delete_url = reverse("item:delete", args=[self.item.pk])
        response = self.client.post(delete_url)

        self.assertRedirects(
            response, f"{reverse('user:login')}?next={delete_url}",
            fetch_redirect_response=False,
        )
        self.assertTrue(Item.objects.filter(pk=self.item.pk).exists())

    def test_delete_item_by_owner(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("item:delete", args=[self.item.pk]))
        messages = [str(message) for message in get_messages(response.wsgi_request)]

        self.assertRedirects(response, reverse("item:list"), fetch_redirect_response=False)
        self.assertEqual(messages, ["Barang berhasil dihapus!"])
        self.assertFalse(Item.objects.filter(pk=self.item.pk).exists())

    def test_delete_item_by_other_user(self):
        self.client.force_login(self.other_user)
        response = self.client.post(reverse("item:delete", args=[self.item.pk]))

        self.assertRedirects(response, reverse("item:detail", args=[self.item.pk]))
        self.assertTrue(Item.objects.filter(pk=self.item.pk).exists())

    def test_delete_with_get_request_does_nothing(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("item:delete", args=[self.item.pk]))

        self.assertRedirects(response, reverse("item:detail", args=[self.item.pk]))
        self.assertTrue(Item.objects.filter(pk=self.item.pk).exists())

    # Geocode

    @patch("item.views.requests.get")
    def test_geocode_address_success(self, mock_get):
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = [{"lat": "-6.40", "lon": "106.82"}]

        self.assertEqual(geocode_address("Depok"), (-6.40, 106.82))
        self.assertEqual(mock_get.call_args.kwargs["timeout"], 5)

    @patch("item.views.requests.get")
    def test_geocode_address_without_result(self, mock_get):
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = []

        self.assertEqual(geocode_address("Tempat Antah Berantah"), (None, None))

    @patch("item.views.requests.get", side_effect=requests.Timeout)
    def test_geocode_address_timeout(self, mock_get):
        self.assertEqual(geocode_address("Depok"), (None, None))

    @patch("item.views.requests.get")
    def test_geocode_empty_address_does_not_call_api(self, mock_get):
        self.assertEqual(geocode_address(""), (None, None))
        mock_get.assert_not_called()