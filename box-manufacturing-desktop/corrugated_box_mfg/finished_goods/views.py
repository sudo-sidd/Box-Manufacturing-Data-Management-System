import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import BoxDetails, BoxPaperRequirements, BoxOrder, MaterialRequirement, ManufacturingCost
from .forms import BoxDetailsForm, BoxPaperRequirementsForm, BoxOrderForm

def get_field_suggestions(request):
    field = request.GET.get('field')
    query = request.GET.get('query', '')

    if not field or not query:
        return JsonResponse({'suggestions': []})
    
    # Get unique values for the requested field
    if hasattr(BoxDetails, field):
        queryset = BoxDetails.objects.filter(
            **{f"{field}__istartswith": query}
        ).values_list(field, flat=True).distinct()[:10]
        
        return JsonResponse({'suggestions': list(queryset)})

    return JsonResponse({'suggestions': []})

class BoxCreateView(CreateView):
    model = BoxDetails
    form_class = BoxDetailsForm
    template_name = 'finished_goods/box_form.html'
    success_url = reverse_lazy('finished_goods:box-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['paper_form'] = BoxPaperRequirementsForm(
                data=self.request.POST
            )
        else:
            context['paper_form'] = BoxPaperRequirementsForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        paper_form = context['paper_form']

        if paper_form.is_valid():
            self.object = form.save()
            paper_requirements = paper_form.save(commit=False)
            paper_requirements.box = self.object
            paper_requirements.save()
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

class BoxListView(ListView):
    model = BoxDetails
    template_name = 'finished_goods/box_list.html'
    context_object_name = 'boxes'
    ordering = ['-created_at']

class BoxDetailView(DetailView):
    model = BoxDetails
    template_name = 'finished_goods/box_detail.html'
    context_object_name = 'box'

class BoxUpdateView(UpdateView):
    model = BoxDetails
    form_class = BoxDetailsForm
    template_name = 'finished_goods/box_form.html'
    success_url = reverse_lazy('finished_goods:box-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Update associated BoxPaperRequirements
        BoxPaperRequirements.objects.update_or_create(
            box=self.object,
            defaults={
                'top_paper_gsm': form.cleaned_data.get('top_paper_gsm', 0),
                'bottom_paper_gsm': form.cleaned_data.get('bottom_paper_gsm', 0)
            }
        )
        return response

def get_box_calculations(request):
    # Get basic box dimensions
    length = float(request.GET.get('length', 0))
    breadth = float(request.GET.get('breadth', 0))
    height = float(request.GET.get('height', 0))
    flute_type = request.GET.get('flute_type', 'B')
    num_plies = int(request.GET.get('num_plies', 3))
    
    # Get paper specifications
    top_paper_gsm = float(request.GET.get('top_paper_gsm', 120))
    bottom_paper_gsm = float(request.GET.get('bottom_paper_gsm', 120))
    
    # Calculate dimensions with shrinkage (as per requirements)
    length_with_shrinkage = length * 1.006
    breadth_with_shrinkage = breadth * 1.006
    height_with_shrinkage = height * 1.0112
    
    # Calculate flute size
    flute_size = (breadth + 0.635) * 1.013575 / 2
    
    # Board size calculations in inches
    full_length_in = ((length + breadth) * 2 + 3.5 + 0.5) / 2.54
    half_length_in = ((length + breadth) + 3.5 + 0.4) / 2.54
    reel_size_1up = ((height + flute_size + flute_size) + 0.8) / 2.54
    reel_size_2up = (((height + flute_size + flute_size) * 2) + 0.8) / 2.54
    reel_size = (breadth + height) / 2.54
    
    # Determine UPS (number of boards to cut from a sheet)
    ups = "Unknown"
    reel_width = (breadth + height) / 2.54
    
    if reel_width < 20:
        ups = "2 board length"
    elif reel_width >= 20 and reel_width < 40:
        ups = "1 board length"
    elif reel_width < 60:
        ups = "full length"
    elif full_length_in > 60:
        ups = "half length"
    
    # Calculate paper weights based on dimensions and GSM
    # For simplicity, assume a standard Take-Up Factor (TUF) of 1.35 for flute papers
    tuf = 1.35
    paper_price = 0.02  # Example price per square meter per GSM
    
    # Weight calculations
    top_paper_weight = (full_length_in * reel_size_1up) * top_paper_gsm * paper_price
    bottom_paper_weight = (full_length_in * reel_size_1up) * bottom_paper_gsm * paper_price
    
    additional_weights = {}
    if num_plies >= 5:
        flute_paper_gsm = float(request.GET.get('flute_paper_gsm', 100))
        additional_weights['flute_paper_weight'] = (full_length_in * reel_size_1up) * flute_paper_gsm * tuf * paper_price
    
    if num_plies == 7:
        flute_paper1_gsm = float(request.GET.get('flute_paper1_gsm', 100))
        middle_paper_gsm = float(request.GET.get('middle_paper_gsm', 100))
        flute_paper2_gsm = float(request.GET.get('flute_paper2_gsm', 100))
        
        additional_weights['flute_paper1_weight'] = (full_length_in * reel_size_1up) * flute_paper1_gsm * tuf * paper_price
        additional_weights['middle_paper_weight'] = (full_length_in * reel_size_1up) * middle_paper_gsm * paper_price
        additional_weights['flute_paper2_weight'] = (full_length_in * reel_size_1up) * flute_paper2_gsm * tuf * paper_price
    
    # Surface area calculation (for reference)
    area = length * breadth * 2 + length * height * 2 + breadth * height * 2
    
    # Cost estimates
    material_cost = top_paper_weight + bottom_paper_weight + sum(additional_weights.values())
    labor_cost = material_cost * 0.3  # 30% of material cost
    total_cost = material_cost + labor_cost
    
    return JsonResponse({
        'dimensions': {
            'length': length_with_shrinkage,
            'breadth': breadth_with_shrinkage,
            'height': height_with_shrinkage,
            'flute_size': flute_size,
        },
        'board_sizes': {
            'full_length_in': full_length_in,
            'half_length_in': half_length_in,
            'reel_size_1up': reel_size_1up,
            'reel_size_2up': reel_size_2up,
            'reel_width': reel_width,
        },
        'ups': ups,
        'paper_weights': {
            'top_paper_weight': round(top_paper_weight, 2),
            'bottom_paper_weight': round(bottom_paper_weight, 2),
            **{k: round(v, 2) for k, v in additional_weights.items()}
        },
        'cost_estimates': {
            'material_cost': round(material_cost, 2),
            'labor_cost': round(labor_cost, 2),
            'total_cost': round(total_cost, 2)
        }
    })

class BoxOrderCreateView(CreateView):
    model = BoxOrder
    form_class = BoxOrderForm
    template_name = 'finished_goods/order_form.html'
    success_url = reverse_lazy('finished_goods:order-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add box templates to the context
        context['box_templates'] = BoxDetails.objects.all()
        
        # If a template is selected in the query params
        if 'template' in self.request.GET:
            try:
                template_id = self.request.GET.get('template')
                context['selected_template'] = BoxDetails.objects.get(id=template_id)
            except (BoxDetails.DoesNotExist, ValueError):
                pass
                
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Calculate and save material requirements
        box_template = form.cleaned_data.get('box_template')
        quantity = form.cleaned_data.get('quantity')
        
        if box_template and quantity:
            # Create material requirements
            materials = self.calculate_materials(box_template, quantity)
            MaterialRequirement.objects.create(
                box_order=self.object,
                **materials
            )
            
            # Create manufacturing cost
            costs = self.calculate_costs(materials, form.cleaned_data.get('profit_margin'))
            ManufacturingCost.objects.create(
                box_order=self.object,
                **costs
            )
            
        return response
    
    def calculate_materials(self, box_template, quantity):
        # This is placeholder logic - replace with your actual calculation logic
        return {
            'top_paper_weight': box_template.area * quantity * 1.1,  # 10% waste
            'bottom_paper_weight': box_template.area * quantity * 0.8,  # Use original field name
            'ink_cost': quantity * 0.05,  # Use original field name
        }
    
    def calculate_costs(self, materials, profit_margin):
        # This is placeholder logic - replace with your actual cost calculations
        material_cost = (materials['top_paper_weight'] * 0.02) + \
                       (materials['bottom_paper_weight'] * 0.015) + \
                       (materials['ink_cost'] * 2)
        
        labor_cost = material_cost * 0.3  # Assume labor is 30% of material cost
        total_cost = material_cost + labor_cost
        suggested_price = total_cost * (1 + (profit_margin / 100))
        
        return {
            'material_cost': material_cost,
            'labor_cost': labor_cost,
            'total_cost': total_cost,
            'profit_margin': profit_margin,
            'suggested_price': suggested_price
        }

def calculate_order_requirements(request):
    template_id = request.GET.get('template_id')
    quantity = int(request.GET.get('quantity', 0))
    margin = float(request.GET.get('margin', 15))
    
    if not template_id or quantity <= 0:
        return JsonResponse({'error': 'Missing or invalid parameters'})
    
    try:
        box_template = BoxDetails.objects.get(id=template_id)
        
        # Calculate material requirements
        requirements = [
            {
                'material_name': 'Kraft Paper',
                'quantity': round(box_template.area * quantity * 1.1, 2),  # 10% waste
                'unit': 'sqm'
            },
            {
                'material_name': 'Corrugated Medium',
                'quantity': round(box_template.area * quantity * 0.8, 2),
                'unit': 'sqm'
            },
            {
                'material_name': 'Adhesive',
                'quantity': round(quantity * 0.05, 2),
                'unit': 'kg'
            }
        ]
        
        # Check inventory status (simplified example)
        inventory_status = {
            'Kraft Paper': 'adequate',
            'Corrugated Medium': 'low',
            'Adhesive': 'adequate'
        }
        
        # Calculate manufacturing costs
        material_cost = sum(item['quantity'] * (2 if item['material_name'] == 'Adhesive' else 0.02) for item in requirements)
        labor_cost = material_cost * 0.3  # Assume labor is 30% of material cost
        total_cost = material_cost + labor_cost
        suggested_price = total_cost * (1 + (margin / 100))
        
        manufacturing_costs = {
            'material_cost': round(material_cost, 2),
            'labor_cost': round(labor_cost, 2),
            'total_cost': round(total_cost, 2),
            'profit_margin': margin,
            'suggested_price': round(suggested_price, 2)
        }
        
        return JsonResponse({
            'requirements': requirements,
            'inventory_status': inventory_status,
            'manufacturing_costs': manufacturing_costs
        })
    except BoxDetails.DoesNotExist:
        return JsonResponse({'error': 'Box template not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

class BoxOrderListView(ListView):
    model = BoxOrder
    template_name = 'finished_goods/order_list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']

class BoxOrderDetailView(DetailView):
    model = BoxOrder
    template_name = 'finished_goods/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        try:
            material_requirements = MaterialRequirement.objects.get(box_order=order)
            context['material_requirements'] = {
                'Kraft Paper': {
                    'quantity': material_requirements.top_paper_weight,
                    'unit': 'sqm',
                    'cost': material_requirements.paper_cost
                },
                'Corrugated Medium': {
                    'quantity': material_requirements.bottom_paper_weight,
                    'unit': 'sqm',
                    'cost': material_requirements.paper_cost * 0.7  # Estimated cost
                },
                'Adhesive': {
                    'quantity': material_requirements.ink_cost,
                    'unit': 'kg',
                    'cost': material_requirements.gum_cost
                }
            }
        except (MaterialRequirement.DoesNotExist, AttributeError):
            pass
        
        try:
            manufacturing_cost = ManufacturingCost.objects.get(box_order=order)
            manufacturing_cost.unit_price = manufacturing_cost.suggested_price / order.quantity if order.quantity else 0
            context['manufacturing_cost'] = manufacturing_cost
        except ManufacturingCost.DoesNotExist:
            pass
            
        return context

@require_POST
def update_order_status(request, order_id):
    try:
        data = json.loads(request.body)
        status = data.get('status')
        
        order = get_object_or_404(BoxOrder, id=order_id)
        order.status = status
        order.save()
        
        return JsonResponse({
            'success': True,
            'status': order.status,
            'status_display': order.get_status_display()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def search_box_template(request):
    query = request.GET.get('q', '')
    if query:
        boxes = BoxDetails.objects.filter(box_name__icontains(query)[:10])
        results = [{
            'id': box.id,
            'name': box.box_name,
            'dimensions': f"{box.length} x {box.breadth} x {box.height}",
            'flute': box.flute_type,
            'plies': box.num_plies
        } for box in boxes]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})