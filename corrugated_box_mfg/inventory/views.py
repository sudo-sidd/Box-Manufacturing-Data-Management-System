from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import PaperReel, PastingGum, Ink, StrappingRoll, PinCoil, Preset, InventoryLog
from decimal import Decimal


def inventory_overview(request):
    context = {
        'paper_reels': PaperReel.objects.all().order_by('-timestamp'),
        'pasting_gum': PastingGum.objects.all().order_by('-timestamp'),
        'ink_stock': Ink.objects.all().order_by('-timestamp'),
        'strapping_rolls': StrappingRoll.objects.all().order_by('-timestamp'),
        'pin_coils': PinCoil.objects.all().order_by('-timestamp'),
        'activity_logs': InventoryLog.objects.all()[:50]  # Show last 50 activities
    }
    return render(request, 'inventory/inventory_overview.html', context)

def inventory_home(request):
    return render(request, "inventory/home.html")


def save_preset(category, value):
    """ Save a unique preset value if it doesn't exist """
    if value and not Preset.objects.filter(category=category, value=value).exists():
        Preset.objects.create(category=category, value=value)

def calculate_prices(quantity, price_per_kg, freight, extra_charges, tax_percent):
    """ Calculate total price excluding tax, tax amount, and final total """
    total_price_ex_tax = (quantity * price_per_kg) + freight + extra_charges
    tax_amount = (total_price_ex_tax * tax_percent) / 100
    total_price = total_price_ex_tax + tax_amount
    return total_price_ex_tax, tax_amount, total_price

def add_inventory(request):
    if request.method == "POST":
        item_type = request.POST.get("item_type")
        company_name = request.POST.get("company_name")

        common_data = {
            "company_name": company_name,
            "price_per_kg": float(request.POST.get("price_per_kg", 0)),
            "freight": float(request.POST.get("freight", 0)),
            "extra_charges": float(request.POST.get("extra_charges", 0)),
            "tax_percent": float(request.POST.get("tax_percent", 0)),
        }

        if item_type == "Paper Reel":
            item = PaperReel.objects.create(
                gsm=request.POST.get("gsm"),
                bf=request.POST.get("bf"),
                size=request.POST.get("size"),
                total_weight=request.POST.get("total_weight"),
                **common_data
            )

        elif item_type == "Pasting Gum":
            item = PastingGum.objects.create(
                gum_type=request.POST.get("gum_type"),
                weight_per_bag=request.POST.get("weight_per_bag"),
                total_qty=request.POST.get("total_qty"),
                **common_data
            )

        elif item_type == "Ink":
            item = Ink.objects.create(
                color=request.POST.get("color"),
                weight_per_can=request.POST.get("weight_per_can"),
                total_qty=request.POST.get("total_qty"),
                **common_data
            )

        elif item_type == "Strapping Roll":
            item = StrappingRoll.objects.create(
                roll_type=request.POST.get("roll_type"),
                meters_per_roll=request.POST.get("meters_per_roll"),
                weight_per_roll=request.POST.get("weight_per_roll"),
                total_qty=request.POST.get("total_qty"),
                **common_data
            )

        elif item_type == "Pin Coil":
            item = PinCoil.objects.create(
                coil_type=request.POST.get("coil_type"),
                total_qty=request.POST.get("total_qty"),
                **common_data
            )

        # Log the action
        details = f"Added {item_type} from {common_data['company_name']}"
        log_inventory_action(item_type, item.id, 'ADD', details)
        
        # Add success message
        messages.success(request, f"{item_type} added successfully!")
        return redirect("inventory_overview")
    return render(request, "inventory/add_inventory.html")

def get_presets(request):
    category = request.GET.get("category")
    presets = Preset.objects.filter(category=category).values_list("value", flat=True)
    return JsonResponse(list(presets), safe=False)

def delete_inventory(request, model_name, item_id):
    # Map URL parameters to model classes
    model_map = {
        'paper_reels': PaperReel,
        'pasting_gum': PastingGum,
        'ink_stock': Ink,
        'strapping_rolls': StrappingRoll,
        'pin_coils': PinCoil
    }
    
    if request.method == 'POST':
        try:
            model = model_map.get(model_name)
            if model:
                item = get_object_or_404(model, id=item_id)
                details = f"Deleted {model_name} - {item.company_name}"
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

def log_inventory_action(item_type, item_id, action, details):
    InventoryLog.objects.create(
        item_type=item_type,
        item_id=item_id,
        action=action,
        details=details
    )
