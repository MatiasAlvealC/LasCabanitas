from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from BD.models import Usuario
from functools import wraps

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
    return render(request, "core/disponibilidad.html")

@admin_required
def inventario(request):
    return render(request, "core/inventario.html")

@admin_required
def mantenciones(request):
    return render(request, "core/mantenciones.html")

def miReserva(request):
    if not request.session.get('usuario_id'):
        messages.error(request, 'Debe iniciar sesión primero')
        return redirect('login')
    return render(request, "core/miReserva.html")

@admin_required
def reservas(request):
    return render(request, "core/reservas.html")

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

@admin_required
def inventario_detalle(request, cabana_id):
    context = {
        'numero_cabana': cabana_id,
    }
    return render(request, "core/inventario_detalle.html", context)