"""Isi database dengan data barang palsu untuk demo dan pengujian manual.

Contoh:
    python manage.py seed_items                 # 55 barang, lengkap dengan foto placeholder
    python manage.py seed_items --count 60
    python manage.py seed_items --no-images     # tanpa foto (lebih cepat)
    python manage.py seed_items --clear         # hapus data demo lama, lalu buat ulang

Semua data demo dimiliki akun demo_1 ... demo_5 (password: demo12345),
sehingga --clear hanya menghapus data demo dan tidak menyentuh data asli.
"""
import io
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from item.grading import calculate_condition_grade, is_eligible
from item.models import Category, Item

DEMO_PREFIX = "demo_"
DEMO_PASSWORD = "demo12345"
DEMO_USER_COUNT = 5

# slug kategori -> daftar (nama barang, deskripsi, harga minimum, harga maksimum per hari)
PRODUCTS = {
    "elektronik": [
        ("Laptop Gaming ASUS ROG", "Laptop gaming RAM 16GB, cocok untuk render dan main game.", 150000, 250000),
        ("MacBook Air M1", "Ringan dan awet baterai, cocok untuk kerja dan kuliah.", 120000, 200000),
        ("Proyektor Epson", "Proyektor 3000 lumens untuk presentasi dan nonton bareng.", 100000, 180000),
        ("Speaker Bluetooth JBL", "Suara jernih dan bass kuat, baterai tahan 12 jam.", 40000, 80000),
        ("Power Bank 20000mAh", "Fast charging, tersedia dua port USB dan satu USB-C.", 15000, 30000),
        ("Monitor 27 Inci", "Monitor IPS resolusi 2K, kabel HDMI sudah termasuk.", 60000, 100000),
        ("Tablet iPad Air", "Layar 10,9 inci, lengkap dengan Apple Pencil.", 80000, 140000),
    ],
    "kamera-fotografi": [
        ("Kamera Mirrorless Sony A6000", "Kamera mirrorless dengan lensa kit 16-50mm.", 150000, 250000),
        ("Kamera DSLR Canon 700D", "Cocok untuk belajar fotografi, termasuk tas dan memory card.", 100000, 180000),
        ("Lensa 50mm f/1.8", "Lensa fix untuk potret dengan bokeh halus.", 50000, 90000),
        ("Tripod Profesional", "Tripod aluminium setinggi 160cm dengan ball head.", 25000, 50000),
        ("Action Cam GoPro", "Tahan air sampai 10 meter, termasuk berbagai mounting.", 70000, 120000),
        ("Drone DJI Mini", "Drone ringan 249 gram, kamera 4K, dua baterai.", 200000, 350000),
        ("Ring Light 18 Inci", "Lampu cincin dengan tripod, tiga mode warna.", 30000, 60000),
    ],
    "alat-outdoor": [
        ("Tenda Dome 4 Orang", "Tenda double layer, anti air, mudah dipasang.", 50000, 90000),
        ("Carrier 60 Liter", "Tas gunung dengan rain cover dan back system nyaman.", 40000, 70000),
        ("Sleeping Bag", "Hangat sampai suhu 10 derajat, bahan ringan.", 20000, 40000),
        ("Kompor Portable", "Kompor gas mini lengkap dengan windshield.", 15000, 30000),
        ("Matras Gulung", "Matras tebal 10mm, ringan dan mudah dibawa.", 10000, 25000),
        ("Headlamp LED", "Terang sampai 300 lumens, bisa diisi ulang.", 10000, 25000),
        ("Hammock Camping", "Hammock dua orang dengan tali pengikat pohon.", 15000, 30000),
    ],
    "perlengkapan-pesta": [
        ("Sound System Portable", "Dua speaker aktif dan satu mixer, cocok untuk acara kecil.", 200000, 400000),
        ("Lampu Sorot LED", "Lampu panggung dengan remote, banyak mode warna.", 50000, 100000),
        ("Tenda Pesta 3x3 Meter", "Tenda lipat dengan rangka besi dan atap anti air.", 100000, 200000),
        ("Kursi Lipat (Isi 20)", "Satu paket 20 kursi lipat, bahan besi dan plastik.", 80000, 150000),
        ("Meja Lipat Panjang", "Meja 180cm, kuat dan mudah dilipat.", 30000, 60000),
        ("Mesin Popcorn", "Mesin popcorn komersial, bisa 5 kg per jam.", 60000, 120000),
        ("Karaoke Set", "Dua mic wireless dan speaker, termasuk aplikasi lagu.", 100000, 180000),
    ],
    "alat-musik": [
        ("Gitar Akustik Yamaha", "Gitar akustik dengan tas dan capo, senar baru.", 40000, 80000),
        ("Keyboard Casio", "61 tuts, ada pilihan ritme, termasuk stand.", 60000, 100000),
        ("Ukulele Soprano", "Ukulele ringan, cocok untuk pemula.", 20000, 40000),
        ("Cajon", "Cajon kayu dengan suara bass yang dalam.", 30000, 60000),
        ("Mic Condenser", "Mic rekaman dengan pop filter dan shock mount.", 40000, 80000),
    ],
    "perkakas": [
        ("Bor Listrik Bosch", "Bor beton dan kayu, dengan satu set mata bor.", 40000, 70000),
        ("Tangga Lipat Aluminium", "Tinggi 2,5 meter, beban maksimal 150 kg.", 30000, 60000),
        ("Mesin Gerinda Tangan", "Gerinda 4 inci, tiga mata gerinda cadangan.", 30000, 60000),
        ("Toolkit Lengkap 120 Pcs", "Kunci pas, obeng, tang, dan perlengkapan lain.", 25000, 50000),
        ("Pompa Air Mini", "Pompa listrik portable untuk kebutuhan rumah.", 35000, 65000),
        ("Genset Mini 1000 Watt", "Genset senyap untuk acara kecil dan camping.", 150000, 250000),
    ],
    "olahraga": [
        ("Sepeda Lipat", "Sepeda lipat 20 inci, 7 percepatan, bisa masuk bagasi.", 60000, 100000),
        ("Raket Badminton Set", "Dua raket dengan tas dan lima shuttlecock.", 20000, 40000),
        ("Bola Futsal", "Bola futsal standar turnamen, sudah dipompa.", 10000, 20000),
        ("Matras Yoga", "Matras anti slip tebal 8mm dengan tali.", 10000, 25000),
        ("Dumbbell Set 20 Kg", "Dumbbell adjustable dengan dua grip.", 30000, 60000),
        ("Papan Skateboard", "Skateboard 8 inci, siap pakai dan lengkap.", 25000, 50000),
    ],
}

CATEGORY_NAMES = {
    "elektronik": "Elektronik",
    "kamera-fotografi": "Kamera & Fotografi",
    "alat-outdoor": "Alat Outdoor",
    "perlengkapan-pesta": "Perlengkapan Pesta",
    "alat-musik": "Alat Musik",
    "perkakas": "Perkakas",
    "olahraga": "Olahraga",
}

# Koordinat tetap supaya seed tidak memanggil Nominatim (ada batas 1 permintaan per detik)
LOCATIONS = [
    ("Depok, Jawa Barat", -6.4025, 106.7942),
    ("Jakarta Selatan", -6.2615, 106.8106),
    ("Bandung, Jawa Barat", -6.9175, 107.6191),
    ("Bogor, Jawa Barat", -6.5971, 106.8060),
    ("Bekasi, Jawa Barat", -6.2383, 106.9756),
    ("Tangerang Selatan, Banten", -6.2886, 106.7179),
    ("Yogyakarta", -7.7956, 110.3695),
    ("Semarang, Jawa Tengah", -6.9932, 110.4203),
    ("Surabaya, Jawa Timur", -7.2575, 112.7521),
]

SUFFIXES = ["", " - Unit B", " - Unit C", " - Unit D"]


class Command(BaseCommand):
    help = "Isi database dengan data barang palsu (akun demo_1..demo_5, password demo12345)."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=55, help="Jumlah barang (default 55)")
        parser.add_argument("--seed", type=int, default=42, help="Angka acak supaya hasilnya bisa diulang")
        parser.add_argument("--no-images", action="store_true", help="Lewati pembuatan foto placeholder")
        parser.add_argument("--clear", action="store_true", help="Hapus data demo lama sebelum membuat yang baru")

    def handle(self, *args, **options):
        if options["count"] < 1:
            self.stderr.write("--count harus minimal 1.")
            return

        demo_items = Item.objects.filter(owner__username__startswith=DEMO_PREFIX)
        if options["clear"]:
            for item in demo_items:
                if item.image:
                    item.image.delete(save=False)  # hapus juga file fotonya dari disk
            deleted_users = User.objects.filter(username__startswith=DEMO_PREFIX).delete()[0]
            self.stdout.write(f"Data demo lama dihapus ({deleted_users} baris, termasuk barangnya).")
        elif demo_items.exists():
            self.stdout.write(
                "Data demo sudah ada. Jalankan dengan --clear untuk membuat ulang, "
                "atau abaikan perintah ini."
            )
            return

        if not Category.objects.exists():
            call_command("loaddata", "categories", verbosity=0)
        categories = {category.slug: category for category in Category.objects.all()}

        rng = random.Random(options["seed"])
        with transaction.atomic():
            users = self.create_demo_users()
            created = self.create_items(rng, users, categories, options["count"], options["no_images"])

        grades = {}
        for item in Item.objects.filter(owner__username__startswith=DEMO_PREFIX):
            grades[item.condition_grade] = grades.get(item.condition_grade, 0) + 1
        self.stdout.write(self.style.SUCCESS(f"{created} barang demo dibuat."))
        for grade, total in sorted(grades.items()):
            self.stdout.write(f"  {grade}: {total}")
        self.stdout.write(f"Login demo: {DEMO_PREFIX}1 ... {DEMO_PREFIX}{DEMO_USER_COUNT}, password {DEMO_PASSWORD}")

    # ------------------------------------------------------------------ helper ---

    def create_demo_users(self):
        users = []
        for number in range(1, DEMO_USER_COUNT + 1):
            user = User(username=f"{DEMO_PREFIX}{number}")
            user.set_password(DEMO_PASSWORD)
            user.save()
            users.append(user)
        return users

    def create_items(self, rng, users, categories, count, no_images):
        catalog = [
            (slug, name, description, low, high)
            for slug, products in PRODUCTS.items()
            if slug in categories
            for name, description, low, high in products
        ]
        rng.shuffle(catalog)

        now = timezone.now()
        created = 0
        for index in range(count):
            slug, name, description, low, high = catalog[index % len(catalog)]
            suffix = SUFFIXES[min(index // len(catalog), len(SUFFIXES) - 1)]
            location, latitude, longitude = rng.choice(LOCATIONS)

            item = Item(
                owner=rng.choice(users),
                category=categories[slug],
                name=name + suffix,
                description=description,
                price_per_day=Decimal(rng.randrange(low, high + 1, 5000)),
                location=location,
                latitude=latitude + rng.uniform(-0.01, 0.01),
                longitude=longitude + rng.uniform(-0.01, 0.01),
                is_available=rng.random() < 0.85,
                **self.random_scores(rng),
            )
            item.full_clean()
            item.condition_grade = calculate_condition_grade(item)
            if not no_images:
                item.image.save(f"demo_{index + 1}.jpg", self.placeholder_image(item.name, slug), save=False)
            item.save()

            # Sebar waktu pembuatan 30 hari ke belakang supaya urutan katalog tidak seragam
            Item.objects.filter(pk=item.pk).update(created_at=now - timedelta(hours=rng.randint(1, 720)))
            created += 1
        return created

    def random_scores(self, rng):
        """Pilih target grade, lalu atur skor. Hanya menghasilkan barang yang layak disewakan."""
        target = rng.choices(["A", "B", "C", "D"], weights=[35, 30, 25, 10])[0]
        scores = {"functional": 4, "physical": 4, "safety": 4, "completeness": 4, "hygiene": 4}
        if target == "B":
            scores[rng.choice(["physical", "completeness"])] = 3
        elif target == "C":
            option = rng.choice(["functional", "safety", "physical", "completeness"])
            scores[option] = 3 if option in ("functional", "safety") else 2
        elif target == "D":
            scores["functional"] = 2
            scores["hygiene"] = rng.choice([3, 4])
        result = {f"{key}_score": value for key, value in scores.items()}
        assert is_eligible(Item(**result))
        return result

    def placeholder_image(self, text, slug):
        from PIL import Image, ImageDraw, ImageFont

        hue = sum(ord(char) for char in slug) % 6
        palette = ["#C9A66B", "#8FB3A0", "#9DB4D1", "#D1A0A0", "#B8A9D1", "#A8C686"]
        image = Image.new("RGB", (640, 420), palette[hue])
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.load_default(size=30)
        except TypeError:  # Pillow lama tidak mendukung parameter size
            font = ImageFont.load_default()
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        draw.text(((640 - (right - left)) / 2, (420 - (bottom - top)) / 2), text, fill="#2A2A1F", font=font)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=80)
        return ContentFile(buffer.getvalue())