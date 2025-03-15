from django.contrib import admin
from .models import (
    # Transaction models
    PaperReel, PastingGum, Ink, StrappingRoll, PinCoil,
    # Summary models
    PaperReelSummary, PastingGumSummary, InkSummary, 
    StrappingRollSummary, PinCoilSummary
)

# Register transaction models
admin.site.register(PaperReel)
admin.site.register(PastingGum)
admin.site.register(Ink)
admin.site.register(StrappingRoll)
admin.site.register(PinCoil)

# Register summary models
admin.site.register(PaperReelSummary)
admin.site.register(PastingGumSummary)
admin.site.register(InkSummary)
admin.site.register(StrappingRollSummary)
admin.site.register(PinCoilSummary)
