from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.urls import reverse

class BoxSpecification(models.Model):
    FLUTE_CHOICES = [
        ('A', 'A Flute'),
        ('B', 'B Flute'),
        ('C', 'C Flute'),
    ]
    PLY_CHOICES = [
        (3, '3 Ply'),
        (5, '5 Ply'),
        (7, '7 Ply'),
    ]
    
    name = models.CharField(max_length=100)
    length = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    breadth = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    height = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    flute_type = models.CharField(max_length=1, choices=FLUTE_CHOICES)
    number_of_plies = models.IntegerField(choices=PLY_CHOICES)
    print_color = models.CharField(max_length=50)
    boxes_ordered = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

class BoxDetails(models.Model):
    FLUTE_CHOICES = [
        ('A', 'A Flute'),
        ('B', 'B Flute'),
        ('C', 'C Flute'),
    ]
    PLY_CHOICES = [
        (3, '3 Ply'),
        (5, '5 Ply'),
        (7, '7 Ply'),
    ]

    box_name = models.CharField(max_length=100, unique=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    breadth = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    height = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    flute_type = models.CharField(max_length=1, choices=FLUTE_CHOICES)
    num_plies = models.IntegerField(choices=PLY_CHOICES)
    print_color = models.CharField(max_length=50)
    order_quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def length_with_shrinkage(self):
        return float(self.length) * 1.006

    @property
    def breadth_with_shrinkage(self):
        return float(self.breadth) * 1.006

    @property
    def height_with_shrinkage(self):
        return float(self.height) * 1.0112

    @property
    def flute_size(self):
        return (float(self.breadth) + 0.635) * 1.013575 / 2

    @property
    def board_length_full(self):
        return ((float(self.length) + float(self.breadth)) * 2 + 3.5 + 0.5) / 2.54

    @property
    def board_length_half(self):
        return (float(self.length) + float(self.breadth) + 3.5 + 0.4) / 2.54

    @property
    def reel_size_1up(self):
        return (float(self.height) + self.flute_size * 2 + 0.8) / 2.54

    @property
    def reel_size_2up(self):
        return ((float(self.height) + self.flute_size * 2) * 2 + 0.8) / 2.54

    @property
    def reel_size(self):
        return (float(self.breadth) + float(self.height)) / 2.54

    @property
    def ups(self):
        bh_inches = (float(self.breadth) + float(self.height)) / 2.54
        lb_inches = ((float(self.length) + float(self.breadth)) * 2 + 3.5 + 0.5) / 2.54
        
        if bh_inches < 20:
            return "2 board length"
        elif bh_inches < 40:
            return "1 board length"
        elif bh_inches < 60:
            return "full length"
        elif lb_inches > 60:
            return "half length"
        return "full length"

class BoxPaperRequirements(models.Model):
    box = models.OneToOneField(BoxDetails, on_delete=models.CASCADE)
    
    # 3 Ply requirements
    top_paper_gsm = models.IntegerField()
    top_paper_bf = models.IntegerField()
    bottom_paper_gsm = models.IntegerField()
    bottom_paper_bf = models.IntegerField()
    
    # Additional fields for 5 Ply
    flute_paper_gsm = models.IntegerField(null=True, blank=True)
    flute_paper_bf = models.IntegerField(null=True, blank=True)
    
    # Additional fields for 7 Ply
    flute_paper1_gsm = models.IntegerField(null=True, blank=True)
    flute_paper1_bf = models.IntegerField(null=True, blank=True)
    middle_paper_gsm = models.IntegerField(null=True, blank=True)
    middle_paper_bf = models.IntegerField(null=True, blank=True)
    flute_paper2_gsm = models.IntegerField(null=True, blank=True)
    flute_paper2_bf = models.IntegerField(null=True, blank=True)

    def calculate_weights(self, paper_price, tuf_factor=1.0):
        l_inches = self.box.board_length_full
        r_inches = self.box.reel_size
        
        weights = {
            'top_paper': (l_inches * r_inches * self.top_paper_gsm * paper_price),
            'bottom_paper': (l_inches * r_inches * self.bottom_paper_gsm * paper_price),
        }
        
        if self.box.num_plies >= 5:
            weights['flute_paper'] = (l_inches * r_inches * self.flute_paper_gsm * tuf_factor)
        
        if self.box.num_plies == 7:
            weights.update({
                'flute_paper1': (l_inches * r_inches * self.flute_paper1_gsm * tuf_factor),
                'middle_paper': (l_inches * r_inches * self.middle_paper_gsm),
                'flute_paper2': (l_inches * r_inches * self.flute_paper2_gsm * tuf_factor),
            })
        
        return weights

class BoxTemplate(models.Model):
    FLUTE_CHOICES = [
        ('A', 'A Flute'),
        ('B', 'B Flute'),
        ('C', 'C Flute'),
    ]
    PLY_CHOICES = [
        (3, '3 Ply'),
        (5, '5 Ply'),
        (7, '7 Ply'),
    ]

    box_name = models.CharField(max_length=100, unique=True)
    length = models.DecimalField(max_digits=10, decimal_places=2)
    breadth = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    flute_type = models.CharField(max_length=1, choices=FLUTE_CHOICES)
    num_plies = models.IntegerField(choices=PLY_CHOICES)
    print_color = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.box_name} ({self.length}×{self.breadth}×{self.height})"

    def get_absolute_url(self):
        return reverse('finished_goods:template-detail', kwargs={'pk': self.pk})

class BoxOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('in_production', 'In Production'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    box_template = models.ForeignKey(BoxTemplate, on_delete=models.PROTECT)
    order_number = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"

class MaterialRequirement(models.Model):
    box_order = models.OneToOneField(BoxOrder, on_delete=models.CASCADE)
    
    # Paper requirements
    top_paper_weight = models.DecimalField(max_digits=10, decimal_places=2)
    bottom_paper_weight = models.DecimalField(max_digits=10, decimal_places=2)
    flute_paper_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    middle_paper_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    # Material costs
    paper_cost = models.DecimalField(max_digits=10, decimal_places=2)
    gum_cost = models.DecimalField(max_digits=10, decimal_places=2)
    ink_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    calculated_at = models.DateTimeField(auto_now=True)

    def calculate_material_costs(self):
        # This will be implemented to calculate costs based on current inventory prices
        pass

class ManufacturingCost(models.Model):
    box_order = models.OneToOneField(BoxOrder, on_delete=models.CASCADE)
    
    # Base material costs
    material_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Manufacturing overhead (for future expansion)
    machine_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overhead_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Pricing
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2)  # in percentage
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_cost(self):
        self.total_cost = (
            self.material_cost +
            self.machine_cost +
            self.labor_cost +
            self.overhead_cost
        )
        return self.total_cost

    def calculate_suggested_price(self):
        total = self.calculate_total_cost()
        self.suggested_price = total * (1 + (self.profit_margin / 100))
        return self.suggested_price