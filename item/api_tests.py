from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .grading import NOT_ELIGIBLE_GRADE
from .models import Category, Item


class ItemAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner_user",
            password="test-password-123",
        )
        self.other_user = User.objects.create_user(
            username="other_user",
            password="test-password-123",
        )
        self.category = Category.objects.create(
            name="Elektronik",
            slug="elektronik",
        )
        self.item = Item.objects.create(
            owner=self.owner,
            category=self.category,
            name="Kamera DSLR",
            description="Kamera kondisi terawat",
            price_per_day=Decimal("75000.00"),
            functional_score=4,
            physical_score=4,
            safety_score=4,
            completeness_score=4,
            hygiene_score=4,
            condition_grade="Grade A — Seperti Baru",
            is_available=True,
            location="Depok",
        )
        self.ineligible_item = Item.objects.create(
            owner=self.owner,
            category=self.category,
            name="Barang Rusak Total",
            description="Tidak layak pakai",
            price_per_day=Decimal("20000.00"),
            functional_score=1,
            physical_score=1,
            safety_score=1,
            completeness_score=1,
            hygiene_score=1,
            condition_grade=NOT_ELIGIBLE_GRADE,
            is_available=False,
            location="Depok",
        )
        self.list_url = reverse("item_api:item-list")
        self.detail_url = reverse("item_api:item-detail", args=[self.item.id])
        self.payload = {
            "category": self.category.id,
            "name": "Speaker Portable",
            "description": "Suara jernih dan baterai awet",
            "price_per_day": "50000.00",
            "functional_score": 4,
            "physical_score": 3,
            "safety_score": 4,
            "completeness_score": 4,
            "hygiene_score": 4,
            "is_available": True,
            "location": "Jakarta Selatan",
        }

    def test_public_list_excludes_ineligible_and_filters_search(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [row["name"] for row in response.data]
        self.assertIn("Kamera DSLR", names)
        self.assertNotIn("Barang Rusak Total", names)

        filtered = self.client.get(self.list_url, {"q": "Kamera"})
        self.assertEqual(filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(len(filtered.data), 1)
        self.assertEqual(filtered.data[0]["name"], "Kamera DSLR")

        empty = self.client.get(self.list_url, {"q": "tidak-ada-barang-ini"})
        self.assertEqual(empty.status_code, status.HTTP_200_OK)
        self.assertEqual(empty.data, [])

    def test_public_detail_and_missing_item_404(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.item.id)
        self.assertEqual(response.data["owner_username"], "owner_user")

        missing_url = reverse("item_api:item-detail", args=[999999])
        missing_resp = self.client.get(missing_url)
        self.assertEqual(missing_resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_cannot_create_update_or_delete(self):
        initial_count = Item.objects.count()
        self.assertEqual(
            self.client.post(self.list_url, self.payload, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.patch(self.detail_url, {"name": "Ubah"}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Item.objects.count(), initial_count)

    def test_non_owner_cannot_patch_or_delete_other_user_item(self):
        self.client.force_authenticate(user=self.other_user)
        self.assertEqual(
            self.client.patch(self.detail_url, {"name": "Dihack"}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, "Kamera DSLR")

    def test_owner_can_create_patch_and_delete_item(self):
        self.client.force_authenticate(user=self.owner)

        create_resp = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        created_id = create_resp.data["id"]
        self.assertEqual(create_resp.data["owner"], self.owner.id)
        self.assertEqual(create_resp.data["condition_grade"], "Grade B — Sangat Baik")

        created_detail_url = reverse("item_api:item-detail", args=[created_id])
        patch_resp = self.client.patch(
            created_detail_url,
            {"name": "Speaker Portable Pro"},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_resp.data["name"], "Speaker Portable Pro")

        delete_resp = self.client.delete(created_detail_url)
        self.assertEqual(delete_resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Item.objects.filter(pk=created_id).exists())

    def test_validation_rejects_invalid_price_and_ineligible_score(self):
        self.client.force_authenticate(user=self.owner)

        bad_price = self.client.post(
            self.list_url,
            {**self.payload, "price_per_day": "0"},
            format="json",
        )
        self.assertEqual(bad_price.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price_per_day", bad_price.data)

        ineligible = self.client.post(
            self.list_url,
            {**self.payload, "safety_score": 1},
            format="json",
        )
        self.assertEqual(ineligible.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_http_method_returns_405(self):
        self.client.force_authenticate(user=self.owner)
        resp = self.client.delete(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        csrf_client = APIClient(enforce_csrf_checks=True)
        logged_in = csrf_client.login(
            username="owner_user",
            password="test-password-123",
        )
        self.assertTrue(logged_in)

        resp = csrf_client.post(self.list_url, self.payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)