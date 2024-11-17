from django.shortcuts import render

# Create your views here.
def home(request):
  return render(request, "core/home.html")

def miReserva(request):
  return render(request, "core/miReserva.html")

def reservas(request):
  return render(request, "core/reservas.html")