# ------------ IMPORTACIONES -----------#
# Librerias Estandar
import json
from datetime import datetime
# Librerias de Django
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string
# Librerias Extras
from xhtml2pdf import pisa
# Importaciones Locales
from .models import Libro, Ejemplar, Genero, Autor, Editorial, Ubicacion
from .forms import LibroForm, EjemplarForm, UbicacionForm
# Importaciones Externas
from loans.models import Prestamo
from recommendation.models import HistorialBusqueda

# ------------ VISTAS ------------------- #

# Interfaz Pública
def catalogo_publico(request):
    query = request.GET.get('q')
    # Capturamos TODOS los parámetros de la URL
    filtros = request.GET.dict()
    filtros.pop('q', None)
    filtros.pop('csrfmiddlewaretoken', None)
    
    if query:
        libros = Libro.objects.filter(
            Q(titulo__icontains=query) | 
            Q(autores__nombre_completo__icontains=query) | 
            Q(generos__nombre__icontains=query)
        ).distinct()
        
        # Guardar en el historial CON LOS FILTROS
        if request.user.is_authenticated:
            HistorialBusqueda.objects.create(
                usuario=request.user, 
                termino_busqueda=query,
                filtros_usados=filtros 
            )
    else:
        libros = Libro.objects.all()
    
    return render(request, 'catalog/lista_publica.html', {'libros': libros})

def detalle_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    disponibles = libro.ejemplares.filter(estado='DISPONIBLE').count()
    prestamos_vencidos = False
    if request.user.is_authenticated:
        prestamos_vencidos = request.user.prestamos.filter(
            estado='APROBADO', 
            fecha_devolucion_esperada__lt=timezone.now().date()
        ).exists()
    puedo_solicitar = disponibles > 0 and not prestamos_vencidos
    context = {
        'libro': libro,
        'ejemplares': libro.ejemplares.all(),
        'disponibles': disponibles,
        'puedo_solicitar': puedo_solicitar,
        'prestamos_vencidos': prestamos_vencidos,
    }
    return render(request, 'catalog/detalle_libro.html', context)

# Gestión Administrativa
@login_required
def gestion_libros(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('catalogo_publico')

    query = request.GET.get('q', '').strip() # Obtenemos parametros de busqueda
    filter_by = request.GET.get('filter_by', 'titulo')
    libros = Libro.objects.all().prefetch_related('autores', 'generos', 'ejemplares').order_by('-id') 
    if query: # Aplica la lógica de filtrado
        if filter_by == 'titulo':
            libros = libros.filter(titulo__icontains=query)
        
        elif filter_by == 'cutter':
            libros = libros.filter(cutter__icontains=query)
            
        elif filter_by == 'autor':
            libros = libros.filter(autores__nombre_completo__icontains=query).distinct()
            
        elif filter_by == 'genero':
            libros = libros.filter(generos__nombre__icontains=query).distinct()
            
        elif filter_by == 'estante':
            libros = libros.filter(ejemplares__ubicacion__estante__icontains=query).distinct()

    return render(request, 'catalog/gestion_libros.html', {
        'libros': libros,
        'query': query,
        'filter_by': filter_by
    })

@login_required
def crear_libro(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('catalogo_publico')
        
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gestion_libros')
    else:
        form = LibroForm()
    return render(request, 'catalog/form_libro.html', {'form': form, 'titulo': 'Registrar Nuevo Libro'})

@login_required
def editar_libro(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    if request.user.perfil.rol != 'ADMIN':
        return redirect('catalogo_publico')
        
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES, instance=libro) #Creamos un formulario asociado al libro existente
        if form.is_valid():
            form.save()
            return redirect('gestion_libros')
    else:
        form = LibroForm(instance=libro)
    return render(request, 'catalog/form_libro.html', {'form': form, 'titulo': 'Editar Libro'})

@login_required
def crear_ejemplar(request):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('catalogo_publico')
        
    if request.method == 'POST':
        form = EjemplarForm(request.POST)
        nombre_ed = request.POST.get('editorial_manual', '').strip()
        if form.is_valid():
            ejemplar = form.save(commit=False)
            
            if nombre_ed:
                editorial_obj, created = Editorial.objects.get_or_create(
                    nombre__iexact=nombre_ed,
                    defaults={'nombre': nombre_ed}
                )
                ejemplar.editorial = editorial_obj
                ejemplar.save()
                messages.success(request, f"Ejemplar registrado con la editorial: {editorial_obj.nombre}")
                return redirect('gestion_libros')
            else:
                messages.error(request, "Por favor, indique el nombre de la editorial.")
    else:
        form = EjemplarForm()
    editoriales = Editorial.objects.all()
    return render(request, 'catalog/form_ejemplar.html', {
        'form': form, 
        'editoriales': editoriales
    })

# API
@login_required
def api_crear_autor(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nuevo = Autor.objects.create(nombre_completo=data.get('nombre'))
        return JsonResponse({'id': nuevo.id, 'nombre': nuevo.nombre_completo})

@login_required
def api_crear_genero(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Aquí integramos el Sistema Dewey
        nuevo = Genero.objects.create(
            nombre=data.get('nombre'),
            codigo_dewey=data.get('dewey')
        )
        return JsonResponse({
            'id': nuevo.id, 
            'nombre': f"{nuevo.codigo_dewey} - {nuevo.nombre}"
        })

# Reportes
@login_required
def portal_reportes(request):
    if request.user.perfil.rol != 'ADMIN': return redirect('home')
    # Obtenemos las salas y estantes únicos para el filtro
    salas = Ejemplar.objects.values('sala').distinct()
    # Una lista de tuplas (Sala, Estante) únicos
    estantes = Ejemplar.objects.values('sala', 'estante').distinct().order_by('sala', 'estante')
    
    return render(request, 'catalog/portal_reportes.html', {
        'salas': salas,
        'estantes': estantes
    })

@login_required
def generar_reporte_estante(request):
    if request.user.perfil.rol != 'ADMIN': return redirect('home')
    
    ubicacion_id = request.GET.get('ubicacion_id')
    ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id)
    
    ejemplares = Ejemplar.objects.filter(ubicacion=ubicacion, estado='DISPONIBLE')
    total_general = ejemplares.count()
    
    desglose = {
        '000': {'n': 'Generalidades', 'c': 0}, '100': {'n': 'Filosofía', 'c': 0},
        '200': {'n': 'Religión', 'c': 0}, '300': {'n': 'Ciencias Sociales', 'c': 0},
        '400': {'n': 'Lenguas', 'c': 0}, '500': {'n': 'Ciencias Puras', 'c': 0},
        '600': {'n': 'Tecnología', 'c': 0}, '700': {'n': 'Artes', 'c': 0},
        '800': {'n': 'Literatura', 'c': 0}, '900': {'n': 'Historia/Geografía', 'c': 0},
        'PV': {'n': 'Poesía Venezolana', 'c': 0},
        'NV': {'n': 'Novela Venezolana', 'c': 0},
        'TV': {'n': 'Teatro Venezolano', 'c': 0},
        'CV': {'n': 'Cuento Venezolano', 'c': 0},
    }

    for ej in ejemplares:
        genero = ej.libro.generos.first()
        if genero and genero.codigo_dewey:
            cod = genero.codigo_dewey.upper().strip()
            if cod in desglose:
                desglose[cod]['c'] += 1
            elif cod[0].isdigit():
                clave = f"{cod[0]}00"
                if clave in desglose:
                    desglose[clave]['c'] += 1

    template_path = 'catalog/reporte_estante_pdf.html' 
    context = {
        'ubicacion': ubicacion,
        'ejemplares': ejemplares,
        'total': total_general,
        'desglose': desglose,
        'fecha': timezone.now()
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Reporte_{ubicacion.sala}.pdf"'
    
    html = render_to_string(template_path, context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err: return HttpResponse('Error PDF')
    return response

@login_required
def gestion_ubicaciones(request):
    if request.user.perfil.rol != 'ADMIN': return redirect('home')
    
    ubicaciones = Ubicacion.objects.all().order_by('sala', 'estante')
    total_ubicaciones = ubicaciones.count()
    
    if request.method == 'POST':
        form = UbicacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Nueva ubicación registrada correctamente.")
            return redirect('gestion_ubicaciones')
    else:
        form = UbicacionForm()
        
    return render(request, 'catalog/gestion_ubicaciones.html', {
        'ubicaciones': ubicaciones,
        'total_ubicaciones': total_ubicaciones,
        'form': form
    })

def lista_ejemplares(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    ejemplares = libro.ejemplares.all()
    return render(request, 'catalog/lista_ejemplares.html', {
        'libro': libro,
        'ejemplares': ejemplares
    })

def editar_ejemplar(request, ejemplar_id):
    ejemplar = get_object_or_404(Ejemplar, id=ejemplar_id)
    ubicaciones = Ubicacion.objects.all()
    
    if request.method == 'POST':
        nuevo_codigo = request.POST.get('codigo')
        nuevo_estado = request.POST.get('estado')
        nueva_ubicacion_id = request.POST.get('ubicacion')
        if nuevo_estado:
            ejemplar.codigo_inventario = nuevo_codigo
            ejemplar.estado = nuevo_estado
            ejemplar.ubicacion_id = nueva_ubicacion_id
            ejemplar.save()
            
            messages.success(request, "Ejemplar actualizado con éxito.")
            return redirect('lista_ejemplares', libro_id=ejemplar.libro.id)
        else:
            messages.error(request, "El campo estado no puede estar vacío.")

    return render(request, 'catalog/editar_ejemplar.html', {
        'ejemplar': ejemplar,
        'ubicaciones': ubicaciones
    })

def obtener_niveles(request):
    estante_nombre = request.GET.get('estante')
    niveles = Ubicacion.objects.filter(estante=estante_nombre).values('id', 'nivel')
    return JsonResponse(list(niveles), safe=False)