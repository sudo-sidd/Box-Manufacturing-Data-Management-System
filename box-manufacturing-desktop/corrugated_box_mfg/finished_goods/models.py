from django.db import models
from django.utils import timezone

class BoxDetails(models.Model):
    FLUTE_CHOICES = [
        ('A', 'A Flute'),
        ('B', 'B Flute'),
        ('C', 'C Flute'),
        ('E', 'E Flute'),
        ('F', 'F Flute'),
        ('BC', 'BC Flute'),
    ]
    
    box_name = models.CharField(max_length=100)
    length = models.DecimalField(max_digits=10, decimal_places=2)
    breadth = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    flute_type = models.CharField(max_length=2, choices=FLUTE_CHOICES)
    num_plies = models.IntegerField(choices=[(3, '3 Ply'), (5, '5 Ply'), (7, '7 Ply')])
    print_color = models.CharField(max_length=50, blank=True)
    order_quantity = models.IntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.box_name} ({self.length}x{self.breadth}x{self.height})"
    
    @property
    def area(self):
        """Calculate the surface area of the box"""
        length = float(self.length)
        breadth = float(self.breadth)
        height = float(self.height)
        return length * breadth * 2 + length * height * 2 + breadth * height * 2

class BoxPaperRequirements(models.Model):
    box = models.OneToOneField(BoxDetails, on_delete=models.CASCADE, related_name='paper_requirements')
    
    # 3 Ply requirements
    top_paper_gsm = models.DecimalField(max_digits=6, decimal_places=2)
    top_paper_bf = models.DecimalField(max_digits=6, decimal_places=2)
    bottom_paper_gsm = models.DecimalField(max_digits=6, decimal_places=2)
    bottom_paper_bf = models.DecimalField(max_digits=6, decimal_places=2)
    
    # 5 Ply additional requirements
    flute_paper_gsm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    flute_paper_bf = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # 7 Ply additional requirements
    flute_paper1_gsm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    flute_paper1_bf = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    middle_paper_gsm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    middle_paper_bf = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    flute_paper2_gsm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    flute_paper2_bf = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Paper Requirements for {self.box}"

class BoxOrder(models.Model):
    STATUS_CHOICES = (
        ('PLACED', 'Order Placed'),
        ('MANUFACTURING', 'Manufacturing'),
        ('PRODUCTION_COMPLETE', 'Production Complete'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('COMPLETED', 'Completed'),
    )
    
    order_number = models.CharField(max_length=20, unique=True)
    customer_name = models.CharField(max_length=100)
    box_template = models.ForeignKey(BoxDetails, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLACED')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"
    
    def get_status_color(self):
        status_colors = {
            'PLACED': 'info',
            'MANUFACTURING': 'primary',
            'PRODUCTION_COMPLETE': 'warning',
            'SHIPPED': 'secondary',
            'DELIVERED': 'success',
            'COMPLETED': 'dark',
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, '')
        
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number like ORD-2023-00001
            last_order = BoxOrder.objects.all().order_by('id').last()
            if not last_order:
                self.order_number = f'ORD-{timezone.now().year}-00001'
            else:
                order_id = int(last_order.order_number.split('-')[-1]) + 1
                self.order_number = f'ORD-{timezone.now().year}-{order_id:05d}'
        super().save(*args, **kwargs)

class MaterialRequirement(models.Model):
    box_order = models.OneToOneField(BoxOrder, on_delete=models.CASCADE, related_name='material_requirement')
    top_paper_weight = models.DecimalField(max_digits=10, decimal_places=2)
    bottom_paper_weight = models.DecimalField(max_digits=10, decimal_places=2)
    ink_cost = models.DecimalField(max_digits=10, decimal_places=2)
    paper_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gum_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Materials for {self.box_order}"

class ManufacturingCost(models.Model):
    box_order = models.OneToOneField(BoxOrder, on_delete=models.CASCADE, related_name='manufacturing_cost')
    material_cost = models.DecimalField(max_digits=10, decimal_places=2)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2)
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Cost for {self.box_order}"