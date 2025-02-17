from django.db import models

class BoxDetails(models.Model):
    box_name = models.CharField(max_length=100)
    length = models.FloatField()
    breadth = models.FloatField()
    height = models.FloatField()
    flute_type = models.CharField(max_length=50)
    num_plies = models.IntegerField()
    print_color = models.CharField(max_length=50)
    order_quantity = models.IntegerField()

class BoxProductionRequirements(models.Model):
    box = models.ForeignKey(BoxDetails, on_delete=models.CASCADE)
    top_paper_gsm = models.IntegerField()
    flute_paper_gsm = models.IntegerField(null=True, blank=True)
    middle_paper_gsm = models.IntegerField(null=True, blank=True)
    bottom_paper_gsm = models.IntegerField()
