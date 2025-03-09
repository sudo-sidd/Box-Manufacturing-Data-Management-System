from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.urls import reverse_lazy
from .models import BoxDetails, BoxPaperRequirements
from .forms import BoxDetailsForm, BoxPaperRequirementsForm
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