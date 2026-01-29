from django.utils import timezone
from loans.models import Prestamo, Sancion

class VerificarSancionesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_staff:
            perfil = request.user.perfil
            
            # Buscar préstamos vencidos no devueltos
            vencidos = Prestamo.objects.filter(
                usuario=request.user,
                estado='APROBADO',
                fecha_devolucion_esperada__lt=timezone.now().date()
            )
            
            if vencidos.exists():
                # Bloquear usuario automaticamente
                if perfil.estado != 'BLOQUEADO':
                    perfil.estado = 'BLOQUEADO'
                    perfil.save()
                    
                    #Registrar sanción en Historial
                    
                    for p in vencidos:
                        Sancion.objects.get_or_create(
                            usuario=request.user,
                            prestamo_origen=p,
                            defaults={'motivo': f'Retraso automático: {p.ejemplar.libro.titulo}'}
                        )
        response = self.get_response(request)
        return response