from django.db import models
from django.conf import settings
from catalog.models import Ejemplar
from django.contrib.auth.models import User
import uuid
from datetime import timedelta
from django.utils import timezone

# Modelos para los Préstamos

class Prestamo(models.Model):
    ESTADOS = (
        ('SOLICITADO', 'Solicitado'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('DEVUELTO', 'Devuelto'),
        ('VENCIDO', 'Vencido (Con retraso)'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Relación con el usuario (Django User)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prestamos')
    # Relacion con el Ejemplar Fisico
    ejemplar = models.ForeignKey(Ejemplar, on_delete=models.CASCADE, related_name='prestamos')
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_devolucion_esperada = models.DateField(null=True, blank=True)
    fecha_devolucion_real = models.DateField(null=True, blank=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='SOLICITADO')
    observaciones_entrega = models.TextField(blank=True, null=True, help_text="Condición del Libro al devolverlo")
    
    def __str__(self):
        return f"Préstamo de {self.usuario.username} - {self.ejemplar.libro.titulo}"
    
    @property
    def esta_vencido(self):
        # Lógica para determinar si bloquea al usuario
        if self.estado == 'APROBADO' and self.fecha_devolucion_esperada:
            return timezone.now().date() > self.fecha_devolucion_esperada
        return False
    
    class Meta:
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'

class Sancion(models.Model):
    # Registra los castigos por devolver tarde o dañar libros
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sanciones')
    prestamo_origen = models.ForeignKey(Prestamo, on_delete=models.SET_NULL, null=True, blank=True)
    motivo = models.TextField()
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
def __str__(self):
    return f"Sanción a {self.usuario.username} - {self.motivo}"

class Notificacion(models.Model):
    TIPOS = (
        ('INFO', 'Información General'),
        ('APROBADO', 'Solicitud Aprobada'),
        ('RECHAZADO', 'Solicitud Rechazada'),
        ('ALERTA', 'Alerta / Vencimiento'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    # Este es el campo que falta y causa el Error 500
    tipo = models.CharField(max_length=20, choices=TIPOS, default='INFO')
    leido = models.BooleanField(default=False) 
    enlace = models.CharField(max_length=200, blank=True, null=True, help_text="Link de acción (ej. descargar pdf)")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.get_tipo_display()} para {self.usuario.username}"