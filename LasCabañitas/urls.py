"""LasCabañitas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings



urlpatterns = [
  path('admin/', admin.site.urls),
  path('', views.home, name='home'),
  path('inventario/', views.inventario, name='inventario'),
  path('mantenciones/', views.mantenciones, name='mantenciones'),
  path('inventario/<int:cabana_id>/', views.inventario_detalle, name='inventario_detalle'),
  path('inventario/<int:cabana_id>/agregar/', views.agregar_objeto, name='agregar_objeto'),
  path('misReservas/', views.misReservas, name='misReservas'),
  path('reservas/', views.reservas, name='reservas'),
  path('login/', views.login, name='login'),
  path('logout/', views.logout, name='logout'),
  path('register/', views.register, name='register'),
  path('disponibilidad/', views.disponibilidad, name='disponibilidad'),
  path('cabana/<int:cabana_id>/', views.cabana_detalle, name='cabana_detalle'),

]

if settings.DEBUG:
  from django.conf.urls.static import static
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)