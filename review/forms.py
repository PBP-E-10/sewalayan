from django import forms
from review.models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': "Ceritakan pengalamanmu menyewa barang ini...."}),
        }
        labels = {
            'rating': 'Rating (1-5)',
            'comment': 'Ulasan',
        }