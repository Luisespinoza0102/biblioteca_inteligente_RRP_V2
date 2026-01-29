from django.db import models
from django.contrib.auth.models import User
import uuid

# Modelos para los USUARIOS.

# Opciones para selectores (Enums)

ROLES = (
    ('ADMIN', 'Administrador'),
    ('USUARIO', 'Usuario'),
)

ESTADOS_USUARIOS = (
    ('ACTIVO', 'Activo'),
    ('INACTIVO', 'Inactivo'),
    ('BLOQUEADO', 'Bloqueado'),
    ('PENDIENTE', 'Pendiente de Activación'),
)

class Perfil(models.Model):
    # Usamos UUID como ID principal para mayor seguridad y profesinalismo
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    dni_carnet = models.CharField(max_length=20, unique=True, verbose_name="DNI o Carnet")
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    
    # Roles y Estados
    rol = models.CharField(max_length=10, choices=ROLES, default='USUARIO')
    estado = models.CharField(max_length=20, choices=ESTADOS_USUARIOS, default='PENDIENTE')
    
    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

# Modelo para Referencias Personales (1:N)
class ReferenciaPersonal(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name="referencias")
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    relacion = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.nombre} - ({self.relacion}) de {self.perfil.usuario.username}"

class UsuarioPermitido(models.Model):
    dni = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, max_length=190)
    nombre_completo = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.dni} - {self.nombre_completo}"