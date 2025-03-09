from django import forms
from .models import BoxDetails, BoxPaperRequirements

class BoxDetailsForm(forms.ModelForm):
    class Meta:
        model = BoxDetails
        fields = ['box_name', 'length', 'breadth', 'height', 'flute_type', 
                 'num_plies', 'print_color', 'order_quantity']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['box_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['length'].widget.attrs.update({'class': 'form-control'})
        self.fields['breadth'].widget.attrs.update({'class': 'form-control'})
        self.fields['height'].widget.attrs.update({'class': 'form-control'})
        self.fields['flute_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['num_plies'].widget.attrs.update({
            'class': 'form-control',
            'onchange': 'updatePaperRequirements(this.value)'
        })
        self.fields['print_color'].widget.attrs.update({'class': 'form-control'})
        self.fields['order_quantity'].widget.attrs.update({'class': 'form-control'})

class BoxPaperRequirementsForm(forms.ModelForm):
    class Meta:
        model = BoxPaperRequirements
        exclude = ['box']

    def __init__(self, num_plies=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Always show 3 ply fields
        required_fields = ['top_paper_gsm', 'top_paper_bf', 
                         'bottom_paper_gsm', 'bottom_paper_bf']
        
        if num_plies >= 5:
            required_fields.extend(['flute_paper_gsm', 'flute_paper_bf'])
            
        if num_plies == 7:
            required_fields.extend([
                'flute_paper1_gsm', 'flute_paper1_bf',
                'middle_paper_gsm', 'middle_paper_bf',
                'flute_paper2_gsm', 'flute_paper2_bf'
            ])
            
        # Hide non-required fields
        for field_name, field in self.fields.items():
            if field_name not in required_fields:
                field.widget = forms.HiddenInput()
            else:
                field.widget.attrs.update({'class': 'form-control'})