from django import forms
from review.models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['item', 'rating', 'comment']
        widgets = {
            'item': forms.Select(attrs={'class': 'input'}),
            'rating': forms.NumberInput(attrs={'class': 'input', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'input', 'rows': 4, 'placeholder': "Ceritakan pengalamanmu menyewa barang ini...."}),
        }
        labels = {
            'item': 'Barang',
            'rating': 'Rating (1-5)',
            'comment': 'Ulasan',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_item(self):
        item = self.cleaned_data['item']
        if self.user is not None and item.owner == self.user:
            raise forms.ValidationError('Kamu tidak bisa mengulas barangmu sendiri.')
        return item