from django import forms
from django.forms import ModelForm, Textarea, TextInput

from .models import Item


class ItemForm(ModelForm):
    # Field penilaian dipisah dari field informasi umum (dipakai di item_form.html)
    SCORE_FIELD_NAMES = [
        'functional_score', 'physical_score', 'safety_score',
        'completeness_score', 'hygiene_score',
    ]

    class Meta:
        model = Item
        fields = [
            'name', 'category', 'description', 'price_per_day',
            'functional_score', 'physical_score', 'safety_score',
            'completeness_score', 'hygiene_score',
            'location', 'image', 'is_available',
        ]

        labels = {
            'name': 'Nama Barang',
            'category': 'Kategori',
            'description': 'Deskripsi',
            'price_per_day': 'Harga Sewa per Hari (Rp)',
            'location': 'Alamat / Lokasi',
            'image': 'Foto Barang',
            'is_available': 'Barang tersedia untuk disewa',
        }
        widgets = {
            'name': TextInput(attrs={'class': 'input', 'placeholder': 'Contoh: Speaker Bluetooth JBL'}),
            'description': Textarea(attrs={'class': 'input', 'rows': 4, 'placeholder': 'Jelaskan kondisi dan kelengkapan barang'}),
            'location': TextInput(attrs={'class': 'input', 'placeholder': 'Contoh: Depok, Jawa Barat'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pasang class 'input' ke semua field kecuali checkbox dan file
        for field in self.fields.values():
            if isinstance(field.widget, (forms.CheckboxInput, forms.ClearableFileInput)):
                continue
            classes = field.widget.attrs.get('class', '').split()
            if 'input' not in classes:
                classes.append('input')
            field.widget.attrs['class'] = ' '.join(classes)

        self.fields['category'].empty_label = 'Pilih kategori (opsional)'
        self.fields['price_per_day'].widget.attrs.update({'min': 1, 'step': 1})

    @property
    def general_fields(self):
        return [self[name] for name in self.fields if name not in self.SCORE_FIELD_NAMES]

    @property
    def score_fields(self):
        return [self[name] for name in self.SCORE_FIELD_NAMES if name in self.fields]

    def clean_price_per_day(self):
        price = self.cleaned_data['price_per_day']
        if price <= 0:
            raise forms.ValidationError('Harga sewa harus lebih dari 0.')
        return price