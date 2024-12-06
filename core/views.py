from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.hashers import make_password, check_password
from BD.models import Cabana, Reserva, Inventario, Mantencion, ActividadRecreativa, ReservaActividad
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate
from datetime import datetime, date, timedelta
from django.db.models import Q
import json
from django.contrib.auth import authenticate, login
from .decorators import admin_required




# Decorador para proteger vistas administrativas
def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name='admin').exists():
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return _wrapped_view

def home(request):
    return render(request, "core/home.html")

def disponibilidad(request):
    
  # Obtén todas las cabañas de la base de datos
  cabanas = Cabana.objects.prefetch_related('imagenes').all()
  return render(request, "core/disponibilidad.html", {'cabanas': cabanas})



@login_required(login_url='/login/')  # Redirige a la URL de inicio de sesión
def cabana_detalle(request, cabana_id):
    cabana = get_object_or_404(Cabana, id=cabana_id)
    
    # Obtener todas las reservas confirmadas para esta cabaña
    reservas = Reserva.objects.filter(
        cabana=cabana,
        estado='confirmada',
        fecha_fin__gte=date.today()
    )
    
    # Crear lista de fechas ocupadas
    fechas_ocupadas = []
    for reserva in reservas:
        fecha_actual = reserva.fecha_inicio
        while fecha_actual <= reserva.fecha_fin:
            fechas_ocupadas.append(fecha_actual.strftime('%Y-%m-%d'))
            fecha_actual += timedelta(days=1)
    
    context = {
        'cabana': cabana,
        'today': date.today(),
        'fechas_ocupadas': json.dumps(fechas_ocupadas),
    }
    return render(request, 'core/cabana_detalle.html', context)

@login_required
def crear_reserva(request, cabana_id):
    # Verificar si el usuario ya tiene una reserva confirmada
    tiene_reserva_confirmada = Reserva.objects.filter(
        usuario=request.user,
        estado='confirmada'
    ).exists()

    if tiene_reserva_confirmada:
        messages.error(request, 'No puedes realizar una nueva reserva mientras tengas una reserva confirmada')
        return redirect('misReservas')

    if request.method == 'POST':
        try:
            cabana = get_object_or_404(Cabana, id=cabana_id)
            fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d')
            fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d')
            
            # Verificar si hay reservas que se solapan
            reservas_solapadas = Reserva.objects.filter(
                cabana=cabana,
                estado='confirmada',
                fecha_inicio__lte=fecha_fin,
                fecha_fin__gte=fecha_inicio
            ).exists()
            
            if reservas_solapadas:
                messages.error(request, 'Las fechas seleccionadas no están disponibles')
                return redirect('cabana_detalle', cabana_id=cabana_id)
            
            # Calcular el total como entero
            dias = (fecha_fin - fecha_inicio).days
            monto_total = int(dias * float(cabana.precio))

            # Crear la reserva
            reserva = Reserva.objects.create(
                usuario=request.user,
                cabana=cabana,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                monto_total=monto_total,
                estado='confirmada'
            )
            
            messages.success(request, 'Reserva creada exitosamente')
            return redirect('misReservas')
        except Exception as e:
            messages.error(request, f'Error al crear la reserva: {str(e)}')
            return redirect('cabana_detalle', cabana_id=cabana_id)
    
    return redirect('disponibilidad')

@login_required
def misReservas(request):
    # Obtener reservas confirmadas del usuario
    reservas_confirmadas = Reserva.objects.filter(
        usuario=request.user,
        estado='confirmada'
    )
    
    # Obtener reservas de actividades del usuario
    reservas_actividades = ReservaActividad.objects.filter(
        usuario=request.user,
        estado='confirmada'
    )
    
    # Obtener actividades recreativas disponibles
    actividades = ActividadRecreativa.objects.all()
    
    # Verificar si el usuario puede hacer nuevas reservas
    puede_reservar = not reservas_confirmadas.exists()
    
    context = {
        'reservas': reservas_confirmadas,
        'reservas_actividades': reservas_actividades,
        'actividades': actividades,
        'puede_reservar': puede_reservar
    }
    return render(request, 'core/miReserva.html', context)


@admin_required
def inventario(request):
    cabanas = Cabana.objects.prefetch_related('imagenes').all()
    return render(request, "core/inventario.html", {'cabanas': cabanas})

@admin_required
def inventario_detalle(request, cabana_id):
    cabana = get_object_or_404(Cabana, id=cabana_id)
    inventario = cabana.inventario.all()  # Asume que el modelo Inventario tiene una relación con Cabana
    return render(request, "core/inventario_detalle.html", {'cabana': cabana, 'inventario': inventario})

@admin_required
def agregar_objeto(request, cabana_id):
    cabana = get_object_or_404(Cabana, id=cabana_id)
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        cantidad = request.POST.get('cantidad')
        Inventario.objects.create(cabana=cabana, descripcion=descripcion, cantidad=cantidad)
        messages.success(request, "Objeto agregado con xito")
        return redirect('inventario_detalle', cabana_id=cabana.id)
    return render(request, "core/inventario_nuevo.html", {'cabana': cabana})


@admin_required
def mantenciones(request):
    # Obtener mantenciones programadas y realizadas
    programadas = Mantencion.objects.filter(estado='pendiente').select_related('cabana')
    historial = Mantencion.objects.filter(estado='realizada').select_related('cabana')

    if request.method == 'POST':
        cabana_id = request.POST.get('cabana')
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion')
        fecha_ejecucion = request.POST.get('fecha_ejecucion')
        responsable = request.POST.get('responsable')
        costo_estimado = request.POST.get('costo_estimado')

        try:
            cabana = Cabana.objects.get(id=cabana_id)
            Mantencion.objects.create(
                cabana=cabana,
                tipo=tipo,
                nombre=descripcion,
                fecha_ejecucion=fecha_ejecucion,
                responsable=responsable,
                costo_estimado=costo_estimado,
            )
            messages.success(request, "Mantención programada con éxito")
        except Cabana.DoesNotExist:
            messages.error(request, "La cabaña seleccionada no existe")
        except Exception as e:
            messages.error(request, f"Error al programar la mantención: {str(e)}")

        return redirect('mantenciones')

    cabanas = Cabana.objects.all()  # Para el formulario de selección de cabaña
    return render(request, "core/mantenciones.html", {'programadas': programadas, 'historial': historial, 'cabanas': cabanas})



@admin_required
def reservas(request):
    # Obtener todas las reservas de la base de datos
    todas_las_reservas = Reserva.objects.select_related('usuario', 'cabana').all()
    return render(request, "core/reservas.html", {'reservas': todas_las_reservas})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Guardar el usuario
            user = form.save()
            
            # Asignar el grupo "cliente" al usuario
            cliente_group, created = Group.objects.get_or_create(name='cliente')
            user.groups.add(cliente_group)
            
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesin.')
            return redirect('login')
        else:
            messages.error(request, 'Error en el formulario. Por favor, verifica los datos.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirige a la página de inicio
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


"""
def login(request):
    if request.method == 'POST':
        correo = request.POST.get('email')
        contrasena = request.POST.get('password')
        
        try:
            usuario = Usuario.objects.get(correo=correo)
            if check_password(contrasena, usuario.contrasena):
                request.session['usuario_id'] = usuario.id
                request.session['usuario_rol'] = usuario.rol
                request.session['usuario_nombre'] = usuario.nombre
                
                messages.success(request, f'Bienvenido {usuario.nombre}')
                return redirect('home')
            else:
                messages.error(request, 'Contraseña incorrecta')
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
    
    return render(request, 'core/login.html')

def logout(request):
    request.session.flush()
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('login')

def register(request):
    if request.method == 'POST':
        try:
            correo = request.POST.get('email')
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, 'Este correo electrónico ya está registrado')
                return render(request, 'core/register.html')

            rut = request.POST.get('rut')
            if Usuario.objects.filter(rut=rut).exists():
                messages.error(request, 'Este RUT ya está registrado')
                return render(request, 'core/register.html')

            nuevo_usuario = Usuario(
                nombre=request.POST.get('first_name'),
                apellido_paterno=request.POST.get('last_name'),
                apellido_materno=request.POST.get('second_last_name'),
                correo=correo,
                rut=rut,
                contrasena=make_password(request.POST.get('password1')),
                rol='cliente'
            )
            nuevo_usuario.save()
            
            messages.success(request, 'Usuario registrado exitosamente')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error al registrar: {str(e)}')
    
    return render(request, 'core/register.html')

"""

@login_required
def cancelar_reserva(request, reserva_id):
    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
        
        # Verificar que la reserva esté confirmada
        if reserva.estado == 'confirmada':
            # Cambiar estado a cancelada
            reserva.estado = 'cancelada'
            reserva.save()
            messages.success(request, 'La reserva ha sido cancelada exitosamente.')
        else:
            messages.error(request, 'Solo se pueden cancelar reservas confirmadas.')
            
    return redirect('misReservas')



@login_required
def actividades_recreativas(request):
    actividades = ActividadRecreativa.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')

        # Crear nueva actividad
        ActividadRecreativa.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio
        )

        messages.success(request, 'Actividad recreativa agregada exitosamente.')
        return redirect('actividades_recreativas')  # Redirigir a la misma vista

    return render(request, 'core/actividades_recreativas.html', {'actividades': actividades})  

@login_required
@admin_required
def agregar_actividad(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')

        ActividadRecreativa.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio
        )

        messages.success(request, 'Actividad recreativa agregada exitosamente.')
        return redirect('actividades_recreativas')

    return render(request, 'core/agregar_actividad.html')

@login_required
def reservar_actividad(request):
    if request.method == 'POST':
        actividad_id = request.POST.get('actividad')
        fecha = request.POST.get('fecha_actividad')
        
        try:
            actividad = ActividadRecreativa.objects.get(id=actividad_id)
            
            # Crear la reserva de actividad
            ReservaActividad.objects.create(
                usuario=request.user,
                actividad=actividad,
                fecha=fecha
            )
            
            messages.success(request, 'Actividad reservada exitosamente')
        except ActividadRecreativa.DoesNotExist:
            messages.error(request, 'La actividad seleccionada no existe')
        except Exception as e:
            messages.error(request, f'Error al reservar la actividad: {str(e)}')
            
    return redirect('misReservas')

@login_required
def cancelar_reserva_actividad(request, reserva_id):
    if request.method == 'POST':
        reserva = get_object_or_404(ReservaActividad, id=reserva_id, usuario=request.user)
        
        if reserva.estado == 'confirmada':
            reserva.estado = 'cancelada'
            reserva.save()
            messages.success(request, 'La reserva de actividad ha sido cancelada exitosamente.')
        else:
            messages.error(request, 'Solo se pueden cancelar reservas confirmadas.')
            
    return redirect('misReservas')
