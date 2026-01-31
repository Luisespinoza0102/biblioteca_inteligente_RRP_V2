#------------- IMPORTACIONES ------------------#
# lIBRERIAS ESTANDAR
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.contrib.auth.views import PasswordChangeView 
from django.contrib.messages.views import SuccessMessageMixin 
from django.urls import reverse_lazy 
from django.db.models import Count, Q, Case, When, IntegerField
# IMPORTACIONES LOCALES
from .forms import RegistroUsuarioForm
from .models import UsuarioPermitido, Perfil, ReferenciaPersonal
from loans.models import Prestamo, Notificacion
from catalog.models import Libro
from recommendation.engine import obtener_recomendaciones
from recommendation.models import HistorialBusqueda
from .forms import FotoPerfilForm

# ----------------------- VISTAS -------------------#

# AUTENTICACIÓN
def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            dni_ingresado = form.cleaned_data['dni']
            nombre_ingresado = form.cleaned_data['nombre'] # <--- Extraemos el nombre
            nueva_clave = form.cleaned_data['password']
            nuevo_tel = form.cleaned_data.get('telefono')

            try:
                # Buscamos al usuario pre-creado
                user = User.objects.get(username=dni_ingresado)
                perfil = user.perfil
                user.set_password(nueva_clave)
                user.first_name = nombre_ingresado 
                user.save()

                perfil.estado = 'ACTIVO'
                if nuevo_tel:
                    perfil.telefono = nuevo_tel
                perfil.save()

                messages.success(request, "¡Cuenta activada con éxito!")
                return redirect('login')

            except User.DoesNotExist:
                messages.error(request, "Este DNI no está autorizado.")
        else:
            print(form.errors) 
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'core/registro.html', {'form': form})
# NAVEGACIÓN Y DASHBOARD
@login_required
def dispatch_dashboard(request):
    if request.user.perfil.rol == 'ADMIN': return redirect('dashboard_admin')
    return redirect('dashboard_usuario')

@login_required
def dashboard_usuario(request):
    # Lógica de Recomendación
    recomendados = obtener_recomendaciones(request.user)
    prestamos_activos = Prestamo.objects.filter(usuario=request.user, estado__in=['SOLICITADO', 'APROBADO'])
    
    return render(request, 'core/dashboard_usuario.html', {
        'recomendados': recomendados,
        'prestamos': prestamos_activos
    })

@login_required
def dashboard_admin(request):
    if request.user.perfil.rol != 'ADMIN': return redirect('home')
    # Métricas para el admin
    pendientes = Prestamo.objects.filter(estado='SOLICITADO').count()
    vencidos_count = 0 
    for p in Prestamo.objects.filter(estado='APROBADO'):
        if p.esta_vencido: vencidos_count += 1
    # Buscamos libros que tengan 0 ejemplares DISPONIBLES
    libros_con_stock = Libro.objects.annotate(
        cantidad_disponible=Count(
            'ejemplares',
            filter=Q(ejemplares__estado='DISPONIBLE')
        )
    )
    # Filtramos solo los que están en 0 o nivel crítico (ej. menos de 2)
    libros_alerta = libros_con_stock.filter(cantidad_disponible__lte=1).order_by('cantidad_disponible')
    
    return render(request, 'core/dashboard_admin.html', {
        'libros_alerta': libros_alerta,
        'pendientes': pendientes,
        'vencidos': vencidos_count
    })

# CONFIGURACIÓN DE USUARIOS
@login_required
def gestion_usuarios(request):
    if request.method == 'POST':
        # Captura de datos básicos
        u_dni = request.POST.get('dni')
        u_nombre = request.POST.get('nombre_completo')
        u_email = request.POST.get('email')
        u_dir = request.POST.get('direccion')
        u_tel = request.POST.get('telefono')
        
        # Captura de listas de referencias
        ref_nombres = request.POST.getlist('ref_nombre[]')
        ref_tels = request.POST.getlist('ref_telefono[]')
        ref_rels = request.POST.getlist('ref_relacion[]')

        try:
            with transaction.atomic():
                nuevo_user = User.objects.create_user(
                    username=u_dni, 
                    email=u_email, 
                    password=u_dni,
                    first_name=u_nombre
                )
                
                u_foto = request.FILES.get('foto_perfil')

                perfil = Perfil.objects.create(
                    usuario=nuevo_user,
                    dni_carnet=u_dni,
                    direccion=u_dir,
                    telefono=u_tel,
                    foto_perfil=u_foto,
                    rol='USUARIO',
                    estado='ACTIVO'
                )

                # Guardar Referencias
                for i in range(len(ref_nombres)):
                    if ref_nombres[i].strip(): # Solo si tiene nombre
                        ReferenciaPersonal.objects.create(
                            perfil=perfil,
                            nombre=ref_nombres[i],
                            telefono=ref_tels[i],
                            relacion=ref_rels[i]
                        )

            messages.success(request, f"Usuario {u_nombre} registrado correctamente.")
            return redirect('gestion_usuarios')

        except IntegrityError:
            messages.error(request, f"Error: El DNI {u_dni} ya está en uso.")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")

    usuarios = Perfil.objects.all().select_related('usuario')
    return render(request, 'core/gestion_usuarios.html', {'usuarios': usuarios})


@login_required
def editar_usuario(request, user_id):
    if request.user.perfil.rol != 'ADMIN':
        return redirect('home')

    perfil = get_object_or_404(Perfil, id=user_id)
    usuario = perfil.usuario

    if request.method == 'POST':
        usuario.first_name = request.POST.get('nombre_completo')
        usuario.email = request.POST.get('email')
        usuario.save()

        perfil.telefono = request.POST.get('telefono')
        perfil.direccion = request.POST.get('direccion')
        perfil.rol = request.POST.get('rol')
        perfil.estado = request.POST.get('estado', perfil.estado) 
        if request.FILES.get('foto_perfil'):
            perfil.foto_perfil = request.FILES.get('foto_perfil')

        perfil.save()
        messages.success(request, f"Usuario {usuario.first_name} actualizado.")
        return redirect('gestion_usuarios')

    return render(request, 'core/editar_usuario.html', {'perfil': perfil})

@login_required
def mi_perfil(request):
    perfil = request.user.perfil
    if request.method == 'POST':
        if request.FILES.get('foto_perfil'):
            perfil.foto_perfil = request.FILES.get('foto_perfil')
            perfil.save()
            messages.success(request, "¡Tu foto de perfil ha sido actualizada!")
            return redirect('mi_perfil')
        else:
            messages.warning(request, "No seleccionaste ninguna imagen.")
    
    return render(request, 'core/perfil.html', {'perfil': perfil})

class CambiarPasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'core/cambiar_password.html'
    success_message = "¡Tu contraseña ha sido actualizada correctamente!"
    
    def get_success_url(self):
        if self.request.user.perfil.rol == 'ADMIN':
            return reverse_lazy('dashboard_admin')
        return reverse_lazy('dashboard_usuario')

# GESTIÓN DE NOTIFICACIONES
@login_required
def mis_notificaciones(request):
    notificaciones = request.user.notificaciones.all().order_by('-fecha')
    response = render(request, 'core/notificaciones.html', {'notificaciones': notificaciones})
    return response

@login_required
def marcar_leida(request, noti_id):
    noti = Notificacion.objects.get(id=noti_id, usuario=request.user)
    noti.leido = True
    noti.save()
    return redirect('mis_notificaciones')

@login_required
def mi_historial(request):
    busquedas = HistorialBusqueda.objects.filter(usuario=request.user).order_by('-fecha')[:20]
    prestamos_pasados = Prestamo.objects.filter(
        usuario=request.user, 
        estado__in=['DEVUELTO']
    ).order_by('-fecha_devolucion_real')

    return render(request, 'core/historial.html', {
        'busquedas': busquedas,
        'prestamos_pasados': prestamos_pasados
    })

# FAKE ADMIN
def vista_error_fake(request):
    return render(request, 'core/fake_404.html', status=404)
