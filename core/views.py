from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.hashers import make_password, check_password
from BD.models import Usuario, Cabana, Reserva, Inventario, Mantencion
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# Decorador para proteger vistas administrativas
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            messages.error(request, 'Debe iniciar sesión primero')
            return redirect('login')
        if request.session.get('usuario_rol') != 'administrador':
            messages.error(request, 'Acceso denegado. Se requieren permisos de administrador.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

def home(request):
    return render(request, "core/home.html")

def disponibilidad(request):
    
  # Obtén todas las cabañas de la base de datos
  cabanas = Cabana.objects.prefetch_related('imagenes').all()
  return render(request, "core/disponibilidad.html", {'cabanas': cabanas})



@login_required(login_url='/login/')  # Redirige a la URL de inicio de sesión
def cabana_detalle(request, cabana_id):
    # Obtener la cabaña
    cabana = get_object_or_404(Cabana, id=cabana_id)

    try:
        # Convertir el usuario autenticado a una instancia del modelo Usuario
        usuario = Usuario.objects.get(id=request.user.id)
    except Usuario.DoesNotExist:
        messages.error(request, "No se encontró un usuario asociado a esta cuenta.")
        return redirect('login')

    if request.method == 'POST':
        # Capturar fechas del formulario
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            try:
                # Crear la reserva
                reserva = Reserva(
                    estado='Confirmada',
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    usuario=usuario,  # Asignar la instancia correcta de usuario
                    cabana=cabana
                )
                reserva.save()
                return redirect('miReserva', reserva_id=reserva.id)
            except Exception as e:
                return render(request, 'core/cabana_detalle.html', {
                    'cabana': cabana,
                    'error': f'Ocurrió un error al crear la reserva: {str(e)}',
                })
        else:
            return render(request, 'core/cabana_detalle.html', {
                'cabana': cabana,
                'error': 'Debe completar todas las fechas.',
            })

    return render(request, 'core/cabana_detalle.html', {'cabana': cabana})

@login_required(login_url='/login/')
def misReservas(request):
    # Obtener el modelo de usuario personalizado
    Usuario = get_user_model()

    try:
        # Obtener al usuario autenticado
        usuario = Usuario.objects.get(id=request.user.id)
    except Usuario.DoesNotExist:
        messages.error(request, "No se encontró un usuario asociado a esta cuenta.")
        return redirect('login')

    # Buscar todas las reservas del usuario
    reservas = Reserva.objects.filter(usuario=usuario)

    if not reservas.exists():
        messages.info(request, "No tienes reservas registradas.")
    
    return render(request, 'core/misReservas.html', {'reservas': reservas})


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
        messages.success(request, "Objeto agregado con éxito")
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

