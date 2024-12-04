from django.db import models
from datetime import timedelta

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, null=True, blank=True)
    correo = models.EmailField(unique=True)
    rut = models.CharField(max_length=12, unique=True, help_text="RUT chileno, formato: 12.345.678-9")
    contrasena = models.CharField(max_length=128)
    rol = models.CharField(
        max_length=50,
        choices=[
            ('administrador', 'Administrador'),
            ('cliente', 'Cliente'),
        ],
        help_text="Rol del usuario dentro del sistema"
    )
    created = models.DateTimeField(auto_now_add = True, verbose_name = "Fech. Creacion")
    updated = models.DateTimeField(auto_now_add = True, verbose_name = "Fech. Edicion")

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"

class Cabana(models.Model):
    ESTADOS_CABANA = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'En mantenimiento'),
    ]

    nombre_cabana = models.CharField(max_length=100)
    capacidad = models.IntegerField(help_text="Capacidad máxima de personas")
    estado = models.CharField(
        max_length=50,
        choices=ESTADOS_CABANA,
        default='disponible',
        help_text="Estado de la cabaña"
    )
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add = True, verbose_name = "Fech. Creacion")
    updated = models.DateTimeField(auto_now_add = True, verbose_name = "Fech. Edicion")

    class Meta:
        verbose_name = "cabaña"
        verbose_name_plural = "cabañas"

    def __str__(self):
        return self.nombre_cabana

class CabanaImage(models.Model):
    cabana = models.ForeignKey(
        Cabana,
        on_delete=models.CASCADE,
        related_name='imagenes',
        verbose_name="Cabaña"
    )
    imagen = models.ImageField(upload_to='images/cabanas/', verbose_name="Imagen de la cabaña")

    class Meta:
        verbose_name = "imagen de cabaña"
        verbose_name_plural = "imágenes de cabaña"

    def __str__(self):
        return f"Imagen de {self.cabana.nombre_cabana}"


class Reserva(models.Model):
    ESTADOS_RESERVA = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]

    estado = models.CharField(
        max_length=50,
        choices=ESTADOS_RESERVA,
        default='pendiente',
        help_text="Estado de la reserva"
    )
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="reservas")
    cabana = models.ForeignKey(Cabana, on_delete=models.CASCADE, related_name="reservas")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fech. Creacion")
    updated = models.DateTimeField(auto_now_add=True, verbose_name="Fech. Edicion")

    class Meta:
        verbose_name = "reserva"
        verbose_name_plural = "reservas"

    def __str__(self):
        return f"Reserva {self.id} - {self.estado}"

    @property
    def noches(self):
        """Calcula el número de noches de la reserva."""
        return (self.fecha_fin - self.fecha_inicio).days

    @property
    def total(self):
        """Calcula el precio total de la reserva."""
        return self.noches * self.cabana.precio


class ActividadRecreativa(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='actividades')
    created = models.DateTimeField(auto_now_add = True, verbose_name = "Fech. Creacion")
    updated = models.DateTimeField(auto_now_add = True, verbose_name = "Fech. Edicion")

    class Meta:
        verbose_name = "actividad recreativa"
        verbose_name_plural = "actividades recreativas"

    def __str__(self):
        return self.nombre

class Inventario(models.Model):
    descripcion = models.CharField(max_length=255)
    cantidad = models.IntegerField()
    cabana = models.ForeignKey(Cabana, on_delete=models.CASCADE, related_name='inventario')
    created = models.DateTimeField(auto_now_add = True, verbose_name = "Fech. Creacion")
    updated = models.DateTimeField(auto_now_add = True, verbose_name = "Fech. Edicion")

    class Meta:
        verbose_name = "inventario"
        verbose_name_plural = "inventarios"

    def __str__(self):
        return self.descripcion



class Mantencion(models.Model):
    TIPOS_MANTENCION = [
        ('preventiva', 'Preventiva'),
        ('correctiva', 'Correctiva'),
    ]

    nombre = models.CharField(max_length=150, help_text="Nombre o descripción de la mantención")
    tipo = models.CharField(max_length=50, choices=TIPOS_MANTENCION, default='preventiva', help_text="Tipo de mantención")
    fecha_ejecucion = models.DateTimeField(help_text="Fecha en la que se realizó la mantención o está programada")
    responsable = models.CharField(max_length=100, help_text="Nombre del responsable de realizar la mantención")
    observaciones = models.TextField(null=True, blank=True, help_text="Detalles u observaciones adicionales")
    costo_estimado = models.DecimalField(max_digits=10, decimal_places=2, help_text="Costo estimado de la mantención", null=True, blank=True)
    cabana = models.ForeignKey(Cabana, on_delete=models.CASCADE, related_name='mantenciones')
    estado = models.CharField(max_length=50, choices=[('pendiente', 'Pendiente'), ('realizada', 'Realizada')], default='pendiente')

    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Mantención"
        verbose_name_plural = "Mantenciones"

    def __str__(self):
        return f"{self.nombre} - {self.fecha_ejecucion} ({self.get_estado_display()})"
