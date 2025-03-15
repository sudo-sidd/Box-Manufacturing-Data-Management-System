from django.db import models
from django.core.validators import MinValueValidator

class PaperReelSummary(models.Model):
    gsm = models.PositiveIntegerField()
    bf = models.CharField(max_length=50)
    size = models.CharField(max_length=50)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_rolls = models.PositiveIntegerField(default=0)
    avg_price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_stock_alert = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    max_stock_alert = models.DecimalField(max_digits=10, decimal_places=2, default=10000)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['gsm', 'bf', 'size']
        verbose_name_plural = "Paper Reel Summaries"

class PastingGumSummary(models.Model):
    gum_type = models.CharField(max_length=100)
    weight_per_bag = models.DecimalField(max_digits=10, decimal_places=2)
    total_bags = models.PositiveIntegerField(default=0)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_stock_alert = models.PositiveIntegerField(default=10)
    max_stock_alert = models.PositiveIntegerField(default=100)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['gum_type', 'weight_per_bag']
        verbose_name_plural = "Pasting Gum Summaries"

class InkSummary(models.Model):
    color = models.CharField(max_length=100)
    weight_per_can = models.DecimalField(max_digits=10, decimal_places=2)
    total_cans = models.PositiveIntegerField(default=0)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_stock_alert = models.PositiveIntegerField(default=5)
    max_stock_alert = models.PositiveIntegerField(default=50)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['color', 'weight_per_can']
        verbose_name_plural = "Ink Summaries"

class StrappingRollSummary(models.Model):
    roll_type = models.CharField(max_length=100)
    meters_per_roll = models.PositiveIntegerField()
    weight_per_roll = models.DecimalField(max_digits=10, decimal_places=2)
    total_rolls = models.PositiveIntegerField(default=0)
    total_meters = models.PositiveIntegerField(default=0)
    avg_price_per_roll = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_stock_alert = models.PositiveIntegerField(default=10)
    max_stock_alert = models.PositiveIntegerField(default=100)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['roll_type', 'meters_per_roll']
        verbose_name_plural = "Strapping Roll Summaries"

class PinCoilSummary(models.Model):
    coil_type = models.CharField(max_length=100)
    total_quantity = models.PositiveIntegerField(default=0)
    avg_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_stock_alert = models.PositiveIntegerField(default=100)
    max_stock_alert = models.PositiveIntegerField(default=1000)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['coil_type']
        verbose_name_plural = "Pin Coil Summaries"

    def __str__(self):
        return f"{self.coil_type} - {self.total_quantity} units"