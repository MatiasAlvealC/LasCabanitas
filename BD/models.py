from django.db import models
from datetime import timedelta
from django.contrib.auth.models import User

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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas')
    cabana = models.ForeignKey('Cabana', on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    monto_total = models.IntegerField(
        help_text="Precio total de la reserva en pesos chilenos"
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('confirmada', 'Confirmada'),
            ('cancelada', 'Cancelada'),
            ('completada', 'Completada')
        ],
        default='confirmada'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'reserva'
        verbose_name_plural = 'reservas'

    def __str__(self):
        return f"Reserva de {self.usuario.username} - {self.cabana.nombre_cabana}"


class ActividadRecreativa(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
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

class ReservaActividad(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas_actividades')
    actividad = models.ForeignKey(ActividadRecreativa, on_delete=models.CASCADE)
    fecha = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=[
            ('confirmada', 'Confirmada'),
            ('cancelada', 'Cancelada'),
            ('completada', 'Completada')
        ],
        default='confirmada'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'reserva de actividad'
        verbose_name_plural = 'reservas de actividades'

    def __str__(self):
        return f"Reserva de {self.actividad.nombre} - {self.usuario.username}"
