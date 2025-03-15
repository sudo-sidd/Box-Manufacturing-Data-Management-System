from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.urls import reverse_lazy
from .models import BoxDetails, BoxPaperRequirements, BoxOrder, MaterialRequirement, ManufacturingCost
from .forms import BoxDetailsForm, BoxPaperRequirementsForm, BoxOrderForm
from django.http import JsonResponse
from django.db.models import Q

def get_field_suggestions(request):
    field = request.GET.get('field')
    query = request.GET.get('query', '')
    
    if not field or not query:
        return JsonResponse({'suggestions': []})
    
    # Get unique values for the requested field
    if hasattr(BoxSpecification, field):
        queryset = BoxSpecification.objects.filter(
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
                num_plies=int(self.request.POST.get('num_plies', 3)),
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
        # Update associated BoxProductionRequirements
        BoxProductionRequirements.objects.update_or_create(
            box=self.object,
            defaults={
                'top_paper_gsm': form.cleaned_data.get('top_paper_gsm', 0),
                'bottom_paper_gsm': form.cleaned_data.get('bottom_paper_gsm', 0)
            }
        )
        return response

def get_box_calculations(request, pk):
    box = BoxDetails.objects.get(pk=pk)
    return JsonResponse({
        'dimensions': {
            'length': box.length_with_shrinkage,
            'breadth': box.breadth_with_shrinkage,
            'height': box.height_with_shrinkage,
            'flute_size': box.flute_size,
        },
        'board_sizes': {
            'full_length': box.board_length_full,
            'half_length': box.board_length_half,
            'reel_size_1up': box.reel_size_1up,
            'reel_size_2up': box.reel_size_2up,
            'reel_size': box.reel_size,
        },
        'ups': box.ups,
    })

class BoxOrderCreateView(CreateView):
    model = BoxOrder
    form_class = BoxOrderForm
    template_name = 'finished_goods/order_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'template_id' in self.request.GET:
            context['selected_template'] = BoxTemplate.objects.get(
                id=self.request.GET['template_id']
            )
        return context

def calculate_order_requirements(request):
    template_id = request.GET.get('template_id')
    quantity = request.GET.get('quantity', 0)
    
    if not template_id or not quantity:
        return JsonResponse({'error': 'Missing parameters'})
    
    template = BoxTemplate.objects.get(id=template_id)
    
    # Calculate material requirements
    requirements = MaterialRequirement.calculate_for_template(template, int(quantity))
    
    # Check inventory status
    inventory_status = check_inventory_status(requirements)
    
    # Calculate manufacturing costs
    costs = calculate_manufacturing_costs(requirements)
    
    return JsonResponse({
        'requirements': requirements,
        'inventory_status': inventory_status,
        'manufacturing_costs': costs
    })

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
        context['material_requirements'] = MaterialRequirement.objects.filter(box_order=order).first()
        context['manufacturing_cost'] = ManufacturingCost.objects.filter(box_order=order).first()
        return context