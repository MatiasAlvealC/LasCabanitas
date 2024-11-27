from django.shortcuts import render
from BD.models import Cabana, Reserva

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404


# Create your views here.
def home(request):
  return render(request, "core/home.html")

def disponibilidad(request):
  # Obtén todas las cabañas de la base de datos
  cabanas = Cabana.objects.prefetch_related('imagenes').all()
  return render(request, "core/disponibilidad.html", {'cabanas': cabanas})

@login_required
def cabana_detalle(request, cabana_id):
    # Obtener la cabaña
    cabana = get_object_or_404(Cabana, id=cabana_id)
    
    if request.method == 'POST':
        # Capturar fechas del formulario
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            # Crear la reserva
            reserva = Reserva(
                estado='pendiente',
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                usuario=request.user,
                cabana=cabana
            )
            reserva.save()
            return redirect('miReserva', reserva_id=reserva.id)
        else:
            return render(request, 'core/cabana_detalle.html', {
                'cabana': cabana,
                'error': 'Debe completar todas las fechas.',
            })
    
    return render(request, 'core/cabana_detalle.html', {'cabana': cabana})

@login_required
def miReserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    return render(request, 'core/miReserva.html', {'reserva': reserva})


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


def reservas(request):
  return render(request, "core/reservas.html")




def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            
            if not remember_me:
                request.session.set_expiry(0)
                
            # Redirigir a la página anterior o a la página principal
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            messages.error(request, 'Correo electrónico o contraseña incorrectos')
            
    return render(request, 'core/login.html')

def logout(request):
    logout(request)
    return redirect('login')




def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        second_last_name = request.POST.get('second_last_name')
        rut = request.POST.get('rut')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'core/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado')
            return render(request, 'core/register.html')

        if not rut or '-' not in rut:
            messages.error(request, 'El formato del RUT no es válido')
            return render(request, 'core/register.html')

        # Crear el nuevo usuario
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name="{last_name} {second_last_name}"
        )

        # Iniciar sesión automáticamente
        login(request, user)
        return redirect('home')

    return render(request, 'core/register.html')