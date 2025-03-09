from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

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