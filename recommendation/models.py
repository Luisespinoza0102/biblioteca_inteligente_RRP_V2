from django.db import models
from django.conf import settings

# Modelos para alimentar el sistema de recomendacion

class HistorialBusqueda(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    termino_busqueda = models.CharField(max_length=255)
    filtros_usados = models.JSONField(default=dict, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario.username} buscó '{self.termino_busqueda}'"

