from django import forms
from .models import BoxDetails, BoxPaperRequirements, BoxOrder, ManufacturingCost

class BoxDetailsForm(forms.ModelForm):
    class Meta:
        model = BoxDetails
        fields = ['box_name', 'length', 'breadth', 'height', 'flute_type', 'num_plies', 'print_color', 'order_quantity']
        widgets = {
            'box_name': forms.TextInput(attrs={'class': 'form-control'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.01'}),
            'breadth': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.01'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.01'}),
            'flute_type': forms.Select(attrs={'class': 'form-control'}),
            'num_plies': forms.Select(attrs={'class': 'form-control', 'id': 'id_num_plies'}),
            'print_color': forms.TextInput(attrs={'class': 'form-control'}),
            'order_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

class BoxPaperRequirementsForm(forms.ModelForm):
    class Meta:
        model = BoxPaperRequirements
        exclude = ['box']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Basic required fields for all ply types
        required_fields = [
            'top_paper_gsm', 'top_paper_bf',
            'bottom_paper_gsm', 'bottom_paper_bf'
        ]
        
        # Get ply type from POST data or instance
        num_plies = 3
        if 'data' in kwargs and kwargs['data'].get('num_plies'):
            num_plies = int(kwargs['data'].get('num_plies'))
        elif kwargs.get('instance') and hasattr(kwargs['instance'], 'box'):
            num_plies = kwargs['instance'].box.num_plies
        
        # Add fields for 5 ply
        if num_plies >= 5:
            required_fields.extend([
                'flute_paper_gsm', 'flute_paper_bf'
            ])
        
        # Add fields for 7 ply
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

    def clean(self):
        cleaned_data = super().clean()
        num_plies = cleaned_data.get('num_plies')
        
        # For 3-ply boxes, only top and bottom paper are required
        # For 5-ply boxes, also require flute_paper
        if num_plies >= 5:
            flute_paper_gsm = cleaned_data.get('flute_paper_gsm')
            flute_paper_bf = cleaned_data.get('flute_paper_bf')
            if not flute_paper_gsm:
                self.add_error('flute_paper_gsm', 'Required for 5-ply boxes')
            if not flute_paper_bf:
                self.add_error('flute_paper_bf', 'Required for 5-ply boxes')
        
        # For 7-ply boxes, also require middle paper and two flute papers
        if num_plies >= 7:
            fields_to_check = [
                'flute_paper1_gsm', 'flute_paper1_bf',
                'middle_paper_gsm', 'middle_paper_bf',
                'flute_paper2_gsm', 'flute_paper2_bf'
            ]
            for field in fields_to_check:
                if not cleaned_data.get(field):
                    self.add_error(field, f'Required for 7-ply boxes')
        
        return cleaned_data

class BoxOrderForm(forms.ModelForm):
    class Meta:
        model = BoxOrder
        fields = ['customer_name', 'box_template', 'quantity', 'profit_margin', 'status', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'box_template': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'profit_margin': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'value': '15.00'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})