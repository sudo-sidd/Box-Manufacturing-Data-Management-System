from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, Avg, Q
from django.contrib.auth.decorators import login_required
from .models import (
    # Transaction Models
    PaperReel, PastingGum, Ink, StrappingRoll, PinCoil,
    # Summary Models
    PaperReelSummary, PastingGumSummary, InkSummary,
    StrappingRollSummary, PinCoilSummary,
    # Other Models
    Preset, InventoryLog
)
from decimal import Decimal
from finished_goods.models import BoxOrder

@login_required
def inventory_overview(request):
    view_type = request.GET.get('view', 'summary')
    context = {
        'view_type': view_type,
        'paper_reels': PaperReelSummary.objects.all() if view_type == 'summary' else PaperReel.objects.all().order_by('-timestamp'),
        'pasting_gum': PastingGumSummary.objects.all() if view_type == 'summary' else PastingGum.objects.all().order_by('-timestamp'),
        'ink_stock': InkSummary.objects.all() if view_type == 'summary' else Ink.objects.all().order_by('-timestamp'),
        'strapping_rolls': StrappingRollSummary.objects.all() if view_type == 'summary' else StrappingRoll.objects.all().order_by('-timestamp'),
        'pin_coils': PinCoilSummary.objects.all() if view_type == 'summary' else PinCoil.objects.all().order_by('-timestamp'),
        'activity_logs': InventoryLog.objects.all()[:50]
    }
    return render(request, 'inventory/inventory_overview.html', context)

@login_required
def get_summary_context():
    """Get aggregated inventory data"""
    return {
        'paper_reels': PaperReelSummary.objects.all(),
        'pasting_gum': PastingGumSummary.objects.all(),
        'ink_stock': InkSummary.objects.all(),
        'strapping_rolls': StrappingRollSummary.objects.all(),
        'pin_coils': PinCoilSummary.objects.all(),
    }

@login_required
def get_transaction_context():
    """Get detailed transaction history"""
    return {
        'paper_reels': PaperReel.objects.all().order_by('-timestamp'),
        'pasting_gum': PastingGum.objects.all().order_by('-timestamp'),
        'ink_stock': Ink.objects.all().order_by('-timestamp'),
        'strapping_rolls': StrappingRoll.objects.all().order_by('-timestamp'),
        'pin_coils': PinCoil.objects.all().order_by('-timestamp'),
    }

def inventory_home(request):
    """Home page with different views for logged-in vs anonymous users"""
    if request.user.is_authenticated:
        # Show the full dashboard for authenticated users
        try:
            from inventory.models import (
                PaperReelSummary, PastingGumSummary, InkSummary, 
                StrappingRollSummary, PinCoilSummary, InventoryLog
            )
            
            context = {
                'title': 'Dashboard',
                'paper_reels': PaperReelSummary.objects.all(),
                'pasting_gum': PastingGumSummary.objects.all(),
                'ink_stock': InkSummary.objects.all(),
                'strapping_rolls': StrappingRollSummary.objects.all(),
                'pin_coils': PinCoilSummary.objects.all(),
                'recent_orders': BoxOrder.objects.all().order_by('-created_at')[:5],
                'activity_logs': InventoryLog.objects.all()[:10],
            }
        except Exception as e:
            # Handle any import or model errors gracefully
            context = {
                'title': 'Dashboard',
                'error_message': f"Could not load dashboard data: {str(e)}"
            }
    else:
        # Show a login prompt for unauthenticated users
        context = {
            'title': 'Welcome to Box Manufacturing CRM',
            'login_required': True
        }
    
    return render(request, 'inventory/home.html', context)

@login_required
def save_preset(category, value):
    """ Save a unique preset value if it doesn't exist """
    if value and not Preset.objects.filter(category=category, value=value).exists():
        Preset.objects.create(category=category, value=value)

@login_required
def calculate_prices(quantity, price_per_kg, freight, extra_charges, tax_percent):
    """ Calculate total price excluding tax, tax amount, and final total """
    total_price_ex_tax = (quantity * price_per_kg) + freight + extra_charges
    tax_amount = (total_price_ex_tax * tax_percent) / 100
    total_price = total_price_ex_tax + tax_amount
    return total_price_ex_tax, tax_amount, total_price

@login_required
def add_inventory(request):
    if request.method == "POST":
        try:
            item_type = request.POST.get("item_type")
            common_data = {
                "company_name": request.POST.get("company_name"),
                "price_per_kg": float(request.POST.get("price_per_kg", 0)),
                "freight": float(request.POST.get("freight", 0)),
                "extra_charges": float(request.POST.get("extra_charges", 0)),
                "tax_percent": float(request.POST.get("tax_percent", 0)),
            }
            # Create item based on type
            if item_type == "Paper Reel":
                item = PaperReel.objects.create(
                    gsm=int(request.POST.get("gsm")),
                    bf=request.POST.get("bf"),
                    size=request.POST.get("size"),
                    total_weight=float(request.POST.get("total_weight")),
                    **common_data
                )
            elif item_type == "Pasting Gum":
                item = PastingGum.objects.create(
                    gum_type=request.POST.get("gum_type"),
                    weight_per_bag=float(request.POST.get("weight_per_bag")),
                    total_qty=int(request.POST.get("total_qty")),
                    **common_data
                )
            elif item_type == "Ink":
                item = Ink.objects.create(
                    color=request.POST.get("color"),
                    weight_per_can=float(request.POST.get("weight_per_can")),
                    total_qty=int(request.POST.get("total_qty")),
                    **common_data
                )
            elif item_type == "Strapping Roll":
                item = StrappingRoll.objects.create(
                    roll_type=request.POST.get("roll_type"),
                    meters_per_roll=int(request.POST.get("meters_per_roll")),
                    weight_per_roll=float(request.POST.get("weight_per_roll")),
                    total_qty=int(request.POST.get("total_qty")),
                    **common_data
                )
            elif item_type == "Pin Coil":
                item = PinCoil.objects.create(
                    coil_type=request.POST.get("coil_type"),
                    total_qty=int(request.POST.get("total_qty")),
                    **common_data
                )
            else:
                raise ValueError(f"Invalid item type: {item_type}")

            # Log the action
            details = f"Added {item_type} from {common_data['company_name']}"
            log_inventory_action(item_type, item.id, 'ADD', details)

            # Update summary tables
            update_summary_tables(item, action='add')
            messages.success(request, f"{item_type} added successfully!")
            return redirect("inventory_overview")
        except Exception as e:
            messages.error(request, f"Error adding inventory: {str(e)}")
            return redirect("add_inventory")
    return render(request, "inventory/add_inventory.html")

@login_required
def get_presets(request):
    category = request.GET.get("category")
    presets = Preset.objects.filter(category=category).values_list("value", flat=True)
    return JsonResponse(list(presets), safe=False)

@login_required
def delete_inventory(request, model_name, item_id):
    # Map URL parameters to model classes
    model_map = {
        'paper_reels': PaperReel,
        'pasting_gum': PastingGum,
        'ink_stock': Ink,
        'strapping_roll': StrappingRoll,
        'pin_coils': PinCoil
    }
    if request.method == 'POST':
        try:
            model = model_map.get(model_name)
            if model:
                item = get_object_or_404(model, id=item_id)
                details = f"Deleted {model_name} - {item.company_name}"
                update_summary_tables(item, 'delete')
                item.delete()
                # Log the action
                log_inventory_action(model_name, item_id, 'DELETE', details)
                return JsonResponse({
                    'status': 'success',
                    'message': f'{model_name.replace("_", " ").title()} deleted successfully'
                })
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid model name'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def edit_inventory(request, model_name, item_id):
    # Map URL parameters to model classes
    model_map = {
        'paper_reels': PaperReel,
        'pasting_gum': PastingGum,
        'ink_stock': Ink,
        'strapping_rolls': StrappingRoll,
        'pin_coils': PinCoil
    }
    model = model_map.get(model_name)
    if not model:
        return JsonResponse({'status': 'error', 'message': 'Invalid model name'})
    item = get_object_or_404(model, id=item_id)
    if request.method == 'POST':
        try:
            # Before updating, subtract old values
            update_summary_tables(item, 'delete')
            # Update common fields
            item.company_name = request.POST.get('company_name')
            item.price_per_kg = Decimal(request.POST.get('price_per_kg'))
            item.freight = Decimal(request.POST.get('freight'))
            item.extra_charges = Decimal(request.POST.get('extra_charges'))
            item.tax_percent = Decimal(request.POST.get('tax_percent'))
            # Update model-specific fields
            if model_name == 'paper_reels':
                item.gsm = int(request.POST.get('gsm'))
                item.bf = request.POST.get('bf')
                item.size = request.POST.get('size')
                item.total_weight = Decimal(request.POST.get('total_weight'))
            elif model_name in ['pasting_gum', 'ink_stock', 'pin_coils']:
                item.total_qty = int(request.POST.get('total_qty'))
                if model_name == 'pasting_gum':
                    item.gum_type = request.POST.get('gum_type')
                    item.weight_per_bag = Decimal(request.POST.get('weight_per_bag'))
                elif model_name == 'ink_stock':
                    item.color = request.POST.get('color')
                    item.weight_per_can = Decimal(request.POST.get('weight_per_can'))
                else:  # pin_coils
                    item.coil_type = request.POST.get('coil_type')
            elif model_name == 'strapping_rolls':
                item.roll_type = request.POST.get('roll_type')
                item.meters_per_roll = int(request.POST.get('meters_per_roll'))
                item.weight_per_roll = Decimal(request.POST.get('weight_per_roll'))
                item.total_qty = int(request.POST.get('total_qty'))
            item.save()  # This will trigger the save method to recalculate totals
            # After updating, add new values
            update_summary_tables(item, 'add')
            # Log the action
            details = f"Modified {model_name} - {item.company_name}"
            log_inventory_action(model_name, item_id, 'EDIT', details)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    # GET request - return current data
    data = {
        'company_name': item.company_name,
        'price_per_kg': str(item.price_per_kg),
        'freight': str(item.freight),
        'extra_charges': str(item.extra_charges),
        'tax_percent': str(item.tax_percent),
    }
    # Add model-specific fields
    if model_name == 'paper_reels':
        data.update({
            'gsm': item.gsm,
            'bf': item.bf,
            'size': item.size,
            'total_weight': str(item.total_weight)
        })
    elif model_name == 'pasting_gum':
        data.update({
            'gum_type': item.gum_type,
            'weight_per_bag': str(item.weight_per_bag),
            'total_qty': item.total_qty
        })
    elif model_name == 'ink_stock':
        data.update({
            'color': item.color,
            'weight_per_can': str(item.weight_per_can),
            'total_qty': item.total_qty
        })
    elif model_name == 'strapping_rolls':
        data.update({
            'roll_type': item.roll_type,
            'meters_per_roll': item.meters_per_roll,
            'weight_per_roll': str(item.weight_per_roll),
            'total_qty': item.total_qty
        })
    elif model_name == 'pin_coils':
        data.update({
            'coil_type': item.coil_type,
            'total_qty': item.total_qty
        })
    return JsonResponse({'status': 'success', 'data': data})

@login_required
def log_inventory_action(item_type, item_id, action, details):
    InventoryLog.objects.create(
        item_type=item_type,
        item_id=item_id,
        action=action,
        details=details
    )

@login_required
def update_summary_tables(instance, action='add'):
    """Update summary tables when transactions occur"""
    if isinstance(instance, PaperReel):
        summary, created = PaperReelSummary.objects.get_or_create(
            gsm=instance.gsm,
            bf=instance.bf,
            size=instance.size,
            defaults={
                'total_weight': Decimal('0.00'),
                'total_rolls': 0,
                'avg_price_per_kg': Decimal('0.00')
            }
        )
        
        if action == 'add':
            summary.total_weight = Decimal(str(summary.total_weight)) + Decimal(str(instance.total_weight))
            summary.total_rolls = int(summary.total_rolls) + 1
        elif action == 'delete':
            if summary.total_rolls > 0 and Decimal(str(summary.total_weight)) >= Decimal(str(instance.total_weight)):
                summary.total_weight = Decimal(str(summary.total_weight)) - Decimal(str(instance.total_weight))
                summary.total_rolls = int(summary.total_rolls) - 1
            else:
                summary.total_weight = Decimal('0.00')
                summary.total_rolls = 0
        
        if summary.total_weight > 0:
            total_items = PaperReel.objects.filter(
                gsm=instance.gsm,
                bf=instance.bf,
                size=instance.size
            )
            avg_price = total_items.aggregate(Avg('price_per_kg'))['price_per_kg__avg']
            summary.avg_price_per_kg = Decimal(str(avg_price)) if avg_price else Decimal('0.00')
        else:
            summary.avg_price_per_kg = Decimal('0.00')
        
        summary.save()

    elif isinstance(instance, PastingGum):
        summary, created = PastingGumSummary.objects.get_or_create(
            gum_type=instance.gum_type,
            weight_per_bag=instance.weight_per_bag,
            defaults={
                'total_bags': 0,
                'total_weight': 0,
                'avg_price_per_kg': 0
            }
        )
        
        if action == 'add':
            summary.total_bags = int(summary.total_bags) + int(instance.total_qty)
            summary.total_weight = float(summary.total_weight) + (float(instance.total_qty) * float(instance.weight_per_bag))
        elif action == 'delete':
            if summary.total_bags >= int(instance.total_qty):
                summary.total_bags = int(summary.total_bags) - int(instance.total_qty)
                summary.total_weight = float(summary.total_weight) - (float(instance.total_qty) * float(instance.weight_per_bag))
            else:
                summary.total_bags = 0
                summary.total_weight = 0
        
        if summary.total_bags > 0:
            total_items = PastingGum.objects.filter(
                gum_type=instance.gum_type,
                weight_per_bag=instance.weight_per_bag
            )
            avg_price = total_items.aggregate(Avg('price_per_kg'))['price_per_kg__avg']
            summary.avg_price_per_kg = float(avg_price) if avg_price else 0
        else:
            summary.avg_price_per_kg = 0
        
        summary.save()

    elif isinstance(instance, Ink):
        summary, created = InkSummary.objects.get_or_create(
            color=instance.color,
            weight_per_can=instance.weight_per_can,
            defaults={
                'total_cans': 0,
                'total_weight': 0,
                'avg_price_per_kg': 0
            }
        )
        
        if action == 'add':
            summary.total_cans = int(summary.total_cans) + int(instance.total_qty)
            summary.total_weight = float(summary.total_weight) + (float(instance.total_qty) * float(instance.weight_per_can))
        elif action == 'delete':
            if summary.total_cans >= int(instance.total_qty):
                summary.total_cans = int(summary.total_cans) - int(instance.total_qty)
                summary.total_weight = float(summary.total_weight) - (float(instance.total_qty) * float(instance.weight_per_can))
            else:
                summary.total_cans = 0
                summary.total_weight = 0
        
        if summary.total_weight > 0:
            total_items = Ink.objects.filter(
                color=instance.color,
                weight_per_can=instance.weight_per_can
            )
            avg_price = total_items.aggregate(Avg('price_per_kg'))['price_per_kg__avg']
            summary.avg_price_per_kg = float(avg_price) if avg_price else 0
        else:
            summary.avg_price_per_kg = 0
        
        summary.save()

    elif isinstance(instance, StrappingRoll):
        summary, created = StrappingRollSummary.objects.get_or_create(
            roll_type=instance.roll_type,
            meters_per_roll=instance.meters_per_roll,
            weight_per_roll=instance.weight_per_roll,
            defaults={
                'total_rolls': 0,
                'total_meters': 0,
                'avg_price_per_roll': 0
            }
        )
        
        if action == 'add':
            summary.total_rolls = int(summary.total_rolls) + int(instance.total_qty)
            summary.total_meters = int(summary.total_meters) + (int(instance.total_qty) * int(instance.meters_per_roll))
        elif action == 'delete':
            if summary.total_rolls >= int(instance.total_qty):
                summary.total_rolls = int(summary.total_rolls) - int(instance.total_qty)
                summary.total_meters = int(summary.total_meters) - (int(instance.total_qty) * int(instance.meters_per_roll))
            else:
                summary.total_rolls = 0
                summary.total_meters = 0
        
        if summary.total_rolls > 0:
            total_items = StrappingRoll.objects.filter(
                roll_type=instance.roll_type,
                meters_per_roll=instance.meters_per_roll
            )
            avg_price = total_items.aggregate(Avg('price_per_kg'))['price_per_kg__avg']
            summary.avg_price_per_roll = float(avg_price) * float(instance.weight_per_roll) if avg_price else 0
        else:
            summary.avg_price_per_roll = 0
        
        summary.save()

    elif isinstance(instance, PinCoil):
        summary, created = PinCoilSummary.objects.get_or_create(
            coil_type=instance.coil_type,
            defaults={
                'total_quantity': 0,
                'avg_price_per_unit': 0
            }
        )
        
        if action == 'add':
            summary.total_quantity = int(summary.total_quantity) + int(instance.total_qty)
        elif action == 'delete':
            if summary.total_quantity >= int(instance.total_qty):
                summary.total_quantity = int(summary.total_quantity) - int(instance.total_qty)
            else:
                summary.total_quantity = 0
        
        if summary.total_quantity > 0:
            total_items = PinCoil.objects.filter(coil_type=instance.coil_type)
            avg_price = total_items.aggregate(Avg('price_per_kg'))['price_per_kg__avg']
            summary.avg_price_per_unit = float(avg_price) if avg_price else 0
        else:
            summary.avg_price_per_unit = 0
        
        summary.save()

@login_required
def get_field_suggestions(request):
    """
    Get suggestions for form fields based on existing data in the database.
    This provides autocomplete functionality for inventory form fields.
    """
    field = request.GET.get('field')
    model_type = request.GET.get('model_type')
    query = request.GET.get('query', '').strip()
    
    print(f"Looking for suggestions: field={field}, model_type={model_type}, query={query}")
    
    # Map URL parameters to model classes
    model_map = {
        'Paper Reel': PaperReel,
        'Pasting Gum': PastingGum,
        'Ink': Ink,
        'Strapping Roll': StrappingRoll,
        'Pin Coil': PinCoil
    }
    
    if not field or not model_type or query == '':
        return JsonResponse({'suggestions': []})
    
    model = model_map.get(model_type)
    if not model:
        return JsonResponse({'suggestions': []})
    
    # Get unique values for the requested field
    try:
        # For numeric fields like gsm, handle them differently
        if field == 'gsm':
            # For numeric fields, we want exact matches at the beginning
            queryset = model.objects.filter(
                **{f"{field}__startswith": query}
            ).values_list(field, flat=True).distinct().order_by(field)[:10]
        else:
            # For text fields, use case-insensitive contains
            queryset = model.objects.filter(
                **{f"{field}__icontains": query}
            ).values_list(field, flat=True).distinct().order_by(field)[:10]
        
        # Convert all values to strings for consistent output
        suggestions = [str(value) for value in queryset]
        
        print(f"Found {len(suggestions)} suggestions for {field}: {suggestions}")
        return JsonResponse({'suggestions': suggestions})
    except Exception as e:
        print(f"Error getting suggestions: {str(e)}")
        return JsonResponse({'suggestions': [], 'error': str(e)})     # Debug log
    field = request.GET.get('field')
    model_type = request.GET.get('model_type')
    query = request.GET.get('query', '')
    
    print(f"Searching for: field={field}, model_type={model_type}, query={query}")  # Debug log
    
    model_map = {
        'Paper Reel': PaperReel,
        'Pasting Gum': PastingGum,
        'Ink': Ink,
        'Strapping Roll': StrappingRoll,
        'Pin Coil': PinCoil
    }
    
    if not field or not query or not model_type:
        return JsonResponse({'suggestions': []})
    
    model = model_map.get(model_type)
    if not model:
        return JsonResponse({'suggestions': []})
    
    # Get unique values for the requested field
    # Use icontains for case-insensitive matching
    queryset = model.objects.filter(
        **{f"{field}__icontains": query}
    ).values_list(field, flat=True).distinct().order_by(field)[:10]
    
    suggestions = list(queryset)
    print(f"Found suggestions: {suggestions}")  # Debug log
    
    return JsonResponse({'suggestions': suggestions})