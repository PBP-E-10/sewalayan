from django import forms
from review.models import Review, Report

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'input', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'input', 'rows': 4, 'placeholder': "Ceritakan pengalamanmu menyewa barang ini...."}),
        }
        labels = {
            'rating': 'Rating (1-5)',
            'comment': 'Ulasan',
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 3, 'placeholder': "Jelaskan masalahnya..."}),
        }
        labels = {
            'reason': 'Alasan',
            'description': 'Keterangan',
        }