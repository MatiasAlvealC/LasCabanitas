from django.contrib import admin

from .models import Cabana, Reserva, ActividadRecreativa, Inventario, Mantencion, CabanaImage

#admin.site.register(Usuario)
admin.site.register(Cabana)
admin.site.register(Reserva)
admin.site.register(ActividadRecreativa)
admin.site.register(Inventario)
admin.site.register(Mantencion)
admin.site.register(CabanaImage)



