from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(category)
admin.site.register(ItmColor)
admin.site.register(ItmSize)
admin.site.register(CartProduct)
admin.site.register(Order)
admin.site.register(item)


