from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages  # Add this import at the top
from .models import PaperReel, PastingGum, Ink, StrappingRoll, PinCoil, Preset


def inventory_overview(request):
    context = {
        'paper_reels': PaperReel.objects.all().order_by('-timestamp'),
        'pasting_gum': PastingGum.objects.all().order_by('-timestamp'),
        'ink_stock': Ink.objects.all().order_by('-timestamp'),
        'strapping_rolls': StrappingRoll.objects.all().order_by('-timestamp'),
        'pin_coils': PinCoil.objects.all().order_by('-timestamp'),
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
            PaperReel.objects.create(
                gsm=request.POST.get("gsm"),
                bf=request.POST.get("bf"),
                size=request.POST.get("size"),
                total_weight=request.POST.get("total_weight"),
                **common_data
            )

        elif item_type == "Pasting Gum":
            PastingGum.objects.create(
                gum_type=request.POST.get("gum_type"),
                weight_per_bag=request.POST.get("weight_per_bag"),
                total_qty=request.POST.get("total_qty"),
                **common_data
            )

        elif item_type == "Ink":
            Ink.objects.create(
                color=request.POST.get("color"),
                weight_per_can=request.POST.get("weight_per_can"),
                total_qty=request.POST.get("total_qty"),
                **common_data
            )

        elif item_type == "Strapping Roll":
            StrappingRoll.objects.create(
                roll_type=request.POST.get("roll_type"),
                meters_per_roll=request.POST.get("meters_per_roll"),
                weight_per_roll=request.POST.get("weight_per_roll"),
                total_qty=request.POST.get("total_qty"),
                **common_data
            )

        elif item_type == "Pin Coil":
            PinCoil.objects.create(
                coil_type=request.POST.get("coil_type"),
                total_qty=request.POST.get("total_qty"),
                **common_data
            )

        # Add success message
        messages.success(request, f"{item_type} added successfully!")
        return redirect("inventory_overview")
    return render(request, "inventory/add_inventory.html")

def get_presets(request):
    category = request.GET.get("category")
    presets = Preset.objects.filter(category=category).values_list("value", flat=True)
    return JsonResponse(list(presets), safe=False)
