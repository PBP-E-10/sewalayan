
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price_per_day', models.DecimalField(decimal_places=2, max_digits=10)),
                ('functional_score', models.IntegerField(choices=[(4, '4 - Sempurna / Optimal'), (3, '3 - Baik / Minor Saja'), (2, '2 - Cukup / Ada Penurunan Performa'), (1, '1 - Buruk / Gagal / Rusak Total')], default=4, verbose_name='Fungsi dan Performa')),
                ('physical_score', models.IntegerField(choices=[(4, '4 - Sempurna / Optimal'), (3, '3 - Baik / Minor Saja'), (2, '2 - Cukup / Ada Penurunan Performa'), (1, '1 - Buruk / Gagal / Rusak Total')], default=4, verbose_name='Kondisi Fisik')),
                ('safety_score', models.IntegerField(choices=[(4, '4 - Sempurna / Optimal'), (3, '3 - Baik / Minor Saja'), (2, '2 - Cukup / Ada Penurunan Performa'), (1, '1 - Buruk / Gagal / Rusak Total')], default=4, verbose_name='Keamanan Penggunaan')),
                ('completeness_score', models.IntegerField(choices=[(4, '4 - Sempurna / Optimal'), (3, '3 - Baik / Minor Saja'), (2, '2 - Cukup / Ada Penurunan Performa'), (1, '1 - Buruk / Gagal / Rusak Total')], default=4, verbose_name='Kelengkapan')),
                ('hygiene_score', models.IntegerField(choices=[(4, '4 - Sempurna / Optimal'), (3, '3 - Baik / Minor Saja'), (2, '2 - Cukup / Ada Penurunan Performa'), (1, '1 - Buruk / Gagal / Rusak Total')], default=4, verbose_name='Kebersihan dan Higienitas')),
                ('condition_grade', models.CharField(blank=True, editable=False, max_length=50)),
                ('is_available', models.BooleanField(default=True)),
                ('location', models.CharField(max_length=255)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='item_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='item.category')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
