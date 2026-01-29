from django.db import models
import uuid


# --------- Modelos para el registro de Libros ------------------- #

# Modelo Autor 
class Autor(models.Model):
    nombre_completo = models.CharField(max_length=150)
    
    def __str__(self):
        return self.nombre_completo

# Modelo Editorial
class Editorial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre

# Modelo Genero
class Genero(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo_dewey = models.CharField(max_length=20, help_text="Ej: 800, Literatura")
    
    def __str__(self):
        return f"{self.codigo_dewey} - {self.nombre}"

# Modelo Libros (esta es la obra intelectual)
class Libro(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=255)
    cutter = models.CharField(max_length=50, help_text="Código Cutter del Autor/titulo")
    descripcion = models.TextField(verbose_name="Sinopsis")
    imagen_portada = models.ImageField(upload_to='libros/', blank=True, null=True)
    
    # Relaciones Muchos a Muchos
    autores = models.ManyToManyField(Autor, related_name='libros')
    generos = models.ManyToManyField(Genero, related_name='libros')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.titulo

# Modelo ubicación (ubicación fisica en los estantes)
class Ubicacion(models.Model):
    SALA_CHOICES = [
        ('ESTADAL', 'Sala Estadal'),
        ('INFANTIL', 'Sala Infantil'),
        ('GENERAL', 'Sala General'),
        ('REFERENCIA', 'Sala de Referencia')
    ]
    sala = models.CharField(max_length=50, choices=SALA_CHOICES)
    estante = models.CharField(max_length=100, help_text="Ej: Estante 1")
    nivel = models.CharField(max_length=100, help_text="Ej: Nivel Superior, Fila 2")
    
    class Meta:
        verbose_name_plural = "Ubicaciones"
        unique_together = ['sala', 'estante', 'nivel']
        
        def __str__(self):
            return f"{self.get_sala_display() - {self.estante} }({self.nivel})"

# Modelo Ejemplar (es la obra física)
class Ejemplar(models.Model):
    ESTADOS_FISICOS = (
        ('DISPONIBLE', 'Disponible'),
        ('PRESTADO', 'Prestado'),
        ('MANTENIMIENTO', 'En Mantenimiento'),
        ('PERDIDO', 'Perdido'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Claves Foráneas
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='ejemplares')
    editorial = models.ForeignKey(Editorial, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='ejemplares')
    codigo_inventario = models.CharField(max_length=50, unique=True, default='', verbose_name='Código de Inventario')
    
    anio_publicacion = models.IntegerField(verbose_name='Año de Publicación')
    estado = models.CharField(max_length=20, choices=ESTADOS_FISICOS, default='DISPONIBLE')
    
    def __str__(self):
        return f"{self.libro.titulo} ({self.anio_publicacion}) - {self.codigo_inventario}"

