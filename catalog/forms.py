from django import forms
from .models import Libro, Ejemplar, Ubicacion

# Formulario de libros
class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'cutter', 'descripcion', 'imagen_portada', 'autores', 'generos']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'cutter': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 3}),
            'autores': forms.SelectMultiple(attrs={'class': 'w-full p-2 border rounded'}),
            'generos': forms.SelectMultiple(attrs={'class': 'w-full p-2 border rounded'}),
            'imagen_portada': forms.FileInput(attrs={'class': 'hidden', 'id': 'input-portada', 'accept': 'image/*'}),
        }

# Formularios de Ejemplares
class EjemplarForm(forms.ModelForm):
    class Meta:
        model = Ejemplar
        fields = ['libro', 'ubicacion', 'codigo_inventario', 'anio_publicacion']
        widgets = {
            'libro': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'ubicacion': forms.Select(attrs={'class': 'w-full bg-slate-900 border-slate-700 text-white p-3 rounded-lg'}),
            'codigo_inventario': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'anio_publicacion': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

# Formularios de Ubicaciones
class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ['sala', 'estante', 'nivel']
        widgets = {
            'sala': forms.Select(attrs={'class': 'w-full bg-slate-900 border-slate-700 text-white rounded-lg p-3'}),
            'estante': forms.TextInput(attrs={'class': 'w-full bg-slate-900 border-slate-700 text-white rounded-lg p-3', 'placeholder': 'Ej: Estante A1'}),
            'nivel': forms.TextInput(attrs={'class': 'w-full bg-slate-900 border-slate-700 text-white rounded-lg p-3', 'placeholder': 'Ej: Fila Superior'}),
        }