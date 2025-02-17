from django.shortcuts import render
from .models import BoxDetails
from django.http import JsonResponse

def add_box_order(request):
    if request.method == "POST":
        box_name = request.POST.get("box_name")
        length = request.POST.get("length")
        breadth = request.POST.get("breadth")
        height = request.POST.get("height")
        flute_type = request.POST.get("flute_type")
        num_plies = request.POST.get("num_plies")
        print_color = request.POST.get("print_color")
        order_quantity = request.POST.get("order_quantity")

        BoxDetails.objects.create(
            box_name=box_name, length=length, breadth=breadth, height=height,
            flute_type=flute_type, num_plies=num_plies, print_color=print_color,
            order_quantity=order_quantity
        )
        return JsonResponse({"message": "Box Order Added Successfully"})
    return render(request, "add_box_order.html")
