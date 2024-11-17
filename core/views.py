from django.shortcuts import render

# Create your views here.
def home(request):
  return render(request, "core/home.html")

def disponibilidad(request):
  return render(request, "core/disponibilidad.html")

def inventario(request):
  return render(request, "core/inventario.html")

def mantenciones(request):
  return render(request, "core/mantenciones.html")

def inventario_detalle(request, cabana_id):
    # Aquí puedes agregar la lógica para obtener los datos reales de la base de datos
    items_ejemplo = [
        {
            'nombre': 'Camas',
            'cantidad': 2,
            'estado': 'Bueno',
            'ultima_revision': '2024-01-15'
        },
        {
            'nombre': 'Sábanas',
            'cantidad': 4,
            'estado': 'Bueno',
            'ultima_revision': '2024-01-15'
        },
        {
            'nombre': 'Toallas',
            'cantidad': 4,
            'estado': 'Regular',
            'ultima_revision': '2024-01-15'
        },
        {
            'nombre': 'Almohadas',
            'cantidad': 4,
            'estado': 'Bueno',
            'ultima_revision': '2024-01-15'
        },
        # ... más items
    ]

    capacidades = {
        1: 2, 2: 2,  # Cabañas 1 y 2: 2 personas
        3: 4, 4: 4,  # Cabañas 3 y 4: 4 personas
        5: 6,        # Cabaña 5: 6 personas
        6: 8         # Cabaña 6: 8 personas
    }

    context = {
        'numero_cabana': cabana_id,
        'capacidad': capacidades.get(cabana_id),
        'items': items_ejemplo
    }
    return render(request, "core/inventario_detalle.html", context)
def miReserva(request):
  return render(request, "core/miReserva.html")

def reservas(request):
  return render(request, "core/reservas.html")
