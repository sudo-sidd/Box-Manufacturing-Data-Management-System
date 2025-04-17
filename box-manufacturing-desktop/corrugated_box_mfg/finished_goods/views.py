import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal

from .models import BoxDetails, BoxPaperRequirements, BoxOrder, MaterialRequirement, ManufacturingCost
from .forms import BoxDetailsForm, BoxPaperRequirementsForm, BoxOrderForm

@login_required
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

class BoxCreateView(LoginRequiredMixin, CreateView):
    model = BoxDetails
    form_class = BoxDetailsForm
    template_name = 'finished_goods/box_form.html'
    success_url = reverse_lazy('finished_goods:box-list')
    login_url = '/accounts/login/'

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

    def get_initial(self):
        initial = super().get_initial()
        initial['num_plies'] = 3  # Default to 3 plies
        return initial

class BoxListView(LoginRequiredMixin, ListView):
    model = BoxDetails
    template_name = 'finished_goods/box_list.html'
    context_object_name = 'boxes'
    ordering = ['-created_at']
    login_url = '/accounts/login/'

class BoxDetailView(LoginRequiredMixin, DetailView):
    model = BoxDetails
    template_name = 'finished_goods/box_detail.html'
    context_object_name = 'box'
    login_url = '/accounts/login/'

class BoxUpdateView(LoginRequiredMixin, UpdateView):
    model = BoxDetails
    form_class = BoxDetailsForm
    template_name = 'finished_goods/box_form.html'
    success_url = reverse_lazy('finished_goods:box-list')
    login_url = '/accounts/login/'

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

@login_required
def get_box_calculations(request):
    # Get basic box dimensions
    length = float(request.GET.get('length', 0))
    breadth = float(request.GET.get('breadth', 0))
    height = float(request.GET.get('height', 0))
    flute_type = request.GET.get('flute_type', 'B')
    num_plies = int(request.GET.get('num_plies', 3))
    
    # Get paper specifications with 0 as default
    top_paper_gsm = float(request.GET.get('top_paper_gsm', 0))
    bottom_paper_gsm = float(request.GET.get('bottom_paper_gsm', 0))
    
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
    
    # FIX: Calculate paper weights based on dimensions and GSM - corrected calculation
    tuf = 1.35  # Take-Up Factor for flute papers
    
    # Calculate surface area in square meters
    # For a box, we need to account for all sides (length, breadth, height)
    # Convert centimeters to meters by dividing by 100
    length_m = length / 100
    breadth_m = breadth / 100
    height_m = height / 100
    
    # Calculate area for each side and total
    top_bottom_area = 2 * (length_m * breadth_m)  # Top and bottom
    side_area_1 = 2 * (length_m * height_m)       # Two sides
    side_area_2 = 2 * (breadth_m * height_m)      # Two sides
    total_area = top_bottom_area + side_area_1 + side_area_2
    
    # Paper weight calculation (GSM = grams per square meter)
    # Weight in kg = (area in m² × GSM) / 1000
    top_paper_weight = (total_area * top_paper_gsm) / 1000
    bottom_paper_weight = (total_area * bottom_paper_gsm) / 1000
    
    # Initialize additional weights
    additional_weights = {}
    
    # Calculate additional paper weights based on ply count
    if num_plies >= 5:
        flute_paper_gsm = float(request.GET.get('flute_paper_gsm', 0))
        # Flute paper uses more material due to corrugation (hence TUF)
        additional_weights['flute_paper_weight'] = (total_area * flute_paper_gsm * tuf) / 1000
    
    if num_plies == 7:
        flute_paper1_gsm = float(request.GET.get('flute_paper1_gsm', 0))
        middle_paper_gsm = float(request.GET.get('middle_paper_gsm', 0))
        flute_paper2_gsm = float(request.GET.get('flute_paper2_gsm', 0))
        
        additional_weights['flute_paper1_weight'] = (total_area * flute_paper1_gsm * tuf) / 1000
        additional_weights['middle_paper_weight'] = (total_area * middle_paper_gsm) / 1000
        additional_weights['flute_paper2_weight'] = (total_area * flute_paper2_gsm * tuf) / 1000
    
    # Calculate total material weight
    total_material_weight = top_paper_weight + bottom_paper_weight + sum(additional_weights.values())
    
    # Cost calculations
    # Assume paper costs ₹80 per kg (adjust as needed)
    paper_cost_per_kg = 80
    material_cost = total_material_weight * paper_cost_per_kg
    labor_cost = material_cost * 0.3  # 30% of material cost
    total_cost = material_cost + labor_cost
    
    # Add more detailed data for the step-by-step calculation
    response_data = {
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
        'total_area': round(total_area, 4),
        'total_material_weight': round(total_material_weight, 2),
        'cost_estimates': {
            'material_cost': round(material_cost, 2),
            'labor_cost': round(labor_cost, 2),
            'total_cost': round(total_cost, 2)
        },
        'constants': {
            'length_shrinkage_factor': 1.006,
            'breadth_shrinkage_factor': 1.006,
            'height_shrinkage_factor': 1.0112,
            'flute_tuf': tuf,
            'paper_cost_per_kg': paper_cost_per_kg,
            'labor_cost_percentage': 0.3
        },
        'formulas': {
            'dimensions': {
                'length': f"{length} × 1.006 = {length_with_shrinkage:.2f} cm",
                'breadth': f"{breadth} × 1.006 = {breadth_with_shrinkage:.2f} cm",
                'height': f"{height} × 1.0112 = {height_with_shrinkage:.2f} cm",
                'flute_size': f"({breadth} + 0.635) × 1.013575 ÷ 2 = {flute_size:.2f} cm",
            },
            'board_sizes': {
                'full_length': f"(({length} + {breadth}) × 2 + 3.5 + 0.5) ÷ 2.54 = {full_length_in:.2f} in",
                'half_length': f"(({length} + {breadth}) + 3.5 + 0.4) ÷ 2.54 = {half_length_in:.2f} in",
                'reel_size_1up': f"(({height} + {flute_size} + {flute_size}) + 0.8) ÷ 2.54 = {reel_size_1up:.2f} in",
                'reel_size_2up': f"((({height} + {flute_size} + {flute_size}) × 2) + 0.8) ÷ 2.54 = {reel_size_2up:.2f} in",
            },
            'surface_area': f"2 × ({length_m:.4f} × {breadth_m:.4f} + {length_m:.4f} × {height_m:.4f} + {breadth_m:.4f} × {height_m:.4f}) = {total_area:.4f} m²",
            'paper_weights': {
                'top_paper': f"{total_area:.4f} × {top_paper_gsm} ÷ 1000 = {top_paper_weight:.2f} kg",
                'bottom_paper': f"{total_area:.4f} × {bottom_paper_gsm} ÷ 1000 = {bottom_paper_weight:.2f} kg",
            },
            'costs': {
                'material_cost': f"{total_material_weight:.2f} × {paper_cost_per_kg} = {material_cost:.2f}",
                'labor_cost': f"{material_cost:.2f} × 0.3 = {labor_cost:.2f}",
                'total_cost': f"{material_cost:.2f} + {labor_cost:.2f} = {total_cost:.2f}"
            }
        }
    }
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Box calculations response data: {response_data}")
    
    return JsonResponse(response_data)

class BoxOrderCreateView(LoginRequiredMixin, CreateView):
    model = BoxOrder
    form_class = BoxOrderForm
    template_name = 'finished_goods/order_form.html'
    success_url = reverse_lazy('finished_goods:order-list')
    login_url = '/accounts/login/'

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
        # Convert materials values to Decimal if they aren't already
        top_paper_weight = Decimal(str(materials['top_paper_weight']))
        bottom_paper_weight = Decimal(str(materials['bottom_paper_weight']))
        ink_cost = Decimal(str(materials['ink_cost']))
        
        # Use Decimal for all calculations
        material_cost = (top_paper_weight * Decimal('0.02')) + \
                       (bottom_paper_weight * Decimal('0.015')) + \
                       (ink_cost * Decimal('2'))
        
        labor_cost = material_cost * Decimal('0.3')  # Assume labor is 30% of material cost
        total_cost = material_cost + labor_cost
        
        # Convert profit_margin to Decimal if it's not already
        if not isinstance(profit_margin, Decimal):
            profit_margin = Decimal(str(profit_margin))
            
        suggested_price = total_cost * (Decimal('1') + (profit_margin / Decimal('100')))
        
        return {
            'material_cost': material_cost,
            'labor_cost': labor_cost,
            'total_cost': total_cost,
            'profit_margin': profit_margin,
            'suggested_price': suggested_price
        }

@login_required
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

class BoxOrderListView(LoginRequiredMixin, ListView):
    model = BoxOrder
    template_name = 'finished_goods/order_list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']
    login_url = '/accounts/login/'

class BoxOrderDetailView(LoginRequiredMixin, DetailView):
    model = BoxOrder
    template_name = 'finished_goods/order_detail.html'
    context_object_name = 'order'
    login_url = '/accounts/login/'

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
                    'cost': material_requirements.paper_cost * Decimal('0.7')  # Estimated cost
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

@login_required
@require_POST
def update_order_status(request, pk):
    try:
        order = BoxOrder.objects.get(pk=pk)
        
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            status = data.get('status')
        else:
            status = request.POST.get('status')
            
        if status in [choice[0] for choice in BoxOrder.STATUS_CHOICES]:
            order.status = status
            order.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Invalid status'})
    except BoxOrder.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

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

def order_details(request, pk):
    order = get_object_or_404(BoxOrder, pk=pk)
    context = {'order': order}
    # Add additional context data as needed
    return render(request, 'finished_goods/includes/order_details.html', context)