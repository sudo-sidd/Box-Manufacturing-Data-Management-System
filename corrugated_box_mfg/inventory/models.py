from django.db import models

class InventorySummary(models.Model):
    item_type = models.CharField(max_length=50)
    gsm = models.PositiveIntegerField(null=True, blank=True)
    total_weight = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item_type} - GSM {self.gsm}"


class Preset(models.Model):
    CATEGORY_CHOICES = [
        ('gsm', 'GSM'),
        ('company', 'Company Name'),
        ('gum_type', 'Gum Type'),
        ('color', 'Ink Color'),
        ('roll_type', 'Strapping Roll Type'),
        ('coil_type', 'Pin Coil Type'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    value = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.get_category_display()}: {self.value}"

class BaseInventory(models.Model):
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    freight = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    extra_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_price_ex_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    company_name = models.CharField(max_length=100, default="Unknown")

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class PaperReel(BaseInventory):
    gsm = models.PositiveIntegerField()
    bf = models.CharField(max_length=50, default="N/A")
    size = models.CharField(max_length=50)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

class PastingGum(BaseInventory):
    gum_type = models.CharField(max_length=50)
    weight_per_bag = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_qty = models.PositiveIntegerField(default=0)

class Ink(BaseInventory):
    color = models.CharField(max_length=50)
    weight_per_can = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_qty = models.PositiveIntegerField(default=0)

class StrappingRoll(BaseInventory):
    roll_type = models.CharField(max_length=50, default="Standard")
    meters_per_roll = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    weight_per_roll = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_qty = models.PositiveIntegerField(default=0)

class PinCoil(BaseInventory):
    coil_type = models.CharField(max_length=50, default="Standard")
    total_qty = models.PositiveIntegerField(default=0)