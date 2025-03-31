from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST

# Import inventory models
from inventory.models import (
    PaperReel, PastingGum, Ink, StrappingRoll, PinCoil,
    PaperReelSummary, PastingGumSummary, InkSummary, StrappingRollSummary, PinCoilSummary,
    InventoryLog
)

# Import finished goods models
from finished_goods.models import BoxOrder, BoxDetails, MaterialRequirement, ManufacturingCost

@user_passes_test(lambda u: u.is_staff)
def cleanup_dashboard(request):
    """Show the cleanup dashboard with stats and cleanup options"""
    
    # Count records in each model for display
    context = {
        'inventory_stats': {
            'paper_reels': PaperReel.objects.count(),
            'pasting_gum': PastingGum.objects.count(),
            'ink': Ink.objects.count(),
            'strapping_roll': StrappingRoll.objects.count(),
            'pin_coil': PinCoil.objects.count(),
            'inventory_logs': InventoryLog.objects.count()
        },
        'orders_stats': {
            'orders': BoxOrder.objects.count(),
            'material_requirements': MaterialRequirement.objects.count(),
            'manufacturing_costs': ManufacturingCost.objects.count()
        },
        'templates_stats': {
            'box_templates': BoxDetails.objects.count()
        }
    }
    
    return render(request, 'data_cleanup/dashboard.html', context)

@require_POST
@user_passes_test(lambda u: u.is_staff)
def clear_inventory(request):
    """Clear all inventory data"""
    if 'confirm' in request.POST:
        # Delete all inventory log entries
        log_count = InventoryLog.objects.count()
        InventoryLog.objects.all().delete()
        
        # Delete all summary records
        summaries_count = (
            PaperReelSummary.objects.count() +
            PastingGumSummary.objects.count() +
            InkSummary.objects.count() +
            StrappingRollSummary.objects.count() +
            PinCoilSummary.objects.count()
        )
        
        PaperReelSummary.objects.all().delete()
        PastingGumSummary.objects.all().delete()
        InkSummary.objects.all().delete()
        StrappingRollSummary.objects.all().delete()
        PinCoilSummary.objects.all().delete()
        
        # Delete all transaction records
        transactions_count = (
            PaperReel.objects.count() +
            PastingGum.objects.count() +
            Ink.objects.count() +
            StrappingRoll.objects.count() +
            PinCoil.objects.count()
        )
        
        PaperReel.objects.all().delete()
        PastingGum.objects.all().delete()
        Ink.objects.all().delete()
        StrappingRoll.objects.all().delete()
        PinCoil.objects.all().delete()
        
        messages.success(
            request, 
            f"Successfully deleted {log_count} logs, {summaries_count} summaries, and {transactions_count} transactions."
        )
    else:
        messages.warning(request, "Confirmation required to clear inventory data.")
    
    return redirect('data_cleanup:dashboard')

@require_POST
@user_passes_test(lambda u: u.is_staff)
def clear_orders(request):
    """Clear all order data"""
    if 'confirm' in request.POST:
        # First delete related data
        mr_count = MaterialRequirement.objects.count()
        mc_count = ManufacturingCost.objects.count()
        MaterialRequirement.objects.all().delete()
        ManufacturingCost.objects.all().delete()
        
        # Then delete orders
        order_count = BoxOrder.objects.count()
        BoxOrder.objects.all().delete()
        
        messages.success(
            request, 
            f"Successfully deleted {order_count} orders, {mr_count} material requirements, and {mc_count} manufacturing costs."
        )
    else:
        messages.warning(request, "Confirmation required to clear order data.")
    
    return redirect('data_cleanup:dashboard')

@require_POST
@user_passes_test(lambda u: u.is_staff)
def clear_templates(request):
    """Clear all box template data"""
    if 'confirm' in request.POST:
        # Check if there are orders that depend on templates
        if BoxOrder.objects.exists():
            messages.error(
                request, 
                "Cannot delete box templates while orders exist. Clear orders first."
            )
        else:
            template_count = BoxDetails.objects.count()
            BoxDetails.objects.all().delete()
            messages.success(request, f"Successfully deleted {template_count} box templates.")
    else:
        messages.warning(request, "Confirmation required to clear template data.")
    
    return redirect('data_cleanup:dashboard')

@require_POST
@user_passes_test(lambda u: u.is_staff)
def clear_all(request):
    """Clear all data (complete system reset)"""
    if 'confirm' in request.POST:
        # First clear orders since they depend on templates
        mr_count = MaterialRequirement.objects.count()
        mc_count = ManufacturingCost.objects.count()
        order_count = BoxOrder.objects.count()
        MaterialRequirement.objects.all().delete()
        ManufacturingCost.objects.all().delete()
        BoxOrder.objects.all().delete()
        
        # Then clear templates
        template_count = BoxDetails.objects.count()
        BoxDetails.objects.all().delete()
        
        # Finally clear inventory
        log_count = InventoryLog.objects.count()
        InventoryLog.objects.all().delete()
        
        PaperReelSummary.objects.all().delete()
        PastingGumSummary.objects.all().delete()
        InkSummary.objects.all().delete()
        StrappingRollSummary.objects.all().delete()
        PinCoilSummary.objects.all().delete()
        
        PaperReel.objects.all().delete()
        PastingGum.objects.all().delete()
        Ink.objects.all().delete()
        StrappingRoll.objects.all().delete()
        PinCoil.objects.all().delete()
        
        messages.success(
            request, 
            f"Complete system reset successful. Deleted {order_count} orders, {template_count} templates, and all inventory data."
        )
    else:
        messages.warning(request, "Confirmation required for complete system reset.")
    
    return redirect('data_cleanup:dashboard')
