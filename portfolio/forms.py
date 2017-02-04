from django import forms


class TransactionForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Quantity', 'type': 'number', 'min': 1}))

class SearchSymbolForm(forms.Form):
    quantity = forms.CharField(
        label='',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Symbol'}))
