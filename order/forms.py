from django.forms import ModelForm, SplitDateTimeField, SplitDateTimeWidget

from order.models import Order


class OrderForm(ModelForm):

    taken_at = SplitDateTimeField(
        label='Waktu ambil barang',
        widget=SplitDateTimeWidget(
            date_attrs={
                'type': 'date',
                'class': 'input flex-1',
                'id': 'taken_at_date'
            },
            time_attrs={'type': 'time', 'class': 'input flex-1'},
        )
    )
    returned_at = SplitDateTimeField(
        label='Waktu kembalian barang',
        widget=SplitDateTimeWidget(
            date_attrs={
                'type': 'date',
                'class': 'input flex-1',
                'id': 'returned_at_date'
            },
            time_attrs={'type': 'time', 'class': 'input flex-1'},
        ),
    )

    class Meta:
        model = Order
        fields = [
            'taken_at', 'returned_at',
        ]
