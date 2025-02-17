from django import forms
from .models import PaperReel, PastingGum

class PaperReelForm(forms.ModelForm):
    class Meta:
        model = PaperReel
        fields = ['gsm', 'size', 'total_weight', 'price_per_kg', 'company_name']

class PastingGumForm(forms.ModelForm):
    class Meta:
        model = PastingGum
        fields = ['gum_type', 'total_qty', 'price_per_kg', 'company_name']
