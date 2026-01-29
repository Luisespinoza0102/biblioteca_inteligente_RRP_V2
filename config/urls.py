from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import dispatch_dashboard # La vista que decide a dónde va el usuario al loguearse

urlpatterns = [
    # Administración de Django (Backend puro)
    path('admin_django/', admin.site.urls),

    # Módulo de Autenticación y Dashboards
    path('', include('core.urls')),

    # Módulo de Catálogo y Libros
    path('catalogo/', include('catalog.urls')),

    # Módulo de Préstamos y Solicitudes
    path('prestamos/', include('loans.urls')),

    # Módulo de Reportes e Inventario
    path('reportes/', include('reports.urls')),

    # Ruta de redirección inteligente después del Login
    path('dashboard/', dispatch_dashboard, name='dispatch_dashboard'),
]

# Configuración para ver las imágenes de los libros en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)