"""
Servicios para la app recetas.
Lógica de negocio reutilizable y operaciones transaccionales.
"""
from django.db import transaction
from django.utils import timezone
from farmasur.models import Receta, RecetaRetenidaISP, UnidosisAsistencial
import hashlib
from datetime import timedelta


class RecetaService:
    """Servicio para gestión de recetas."""
    
    @staticmethod
    @transaction.atomic
    def crear_receta(folio, rut_paciente, nombre_paciente, rut_medico, nombre_medico,
                     fecha_emision, medicamentos, notas='', datos_adicionales=None):
        """Crea una nueva receta."""
        receta = Receta.objects.create(
            folio=folio,
            rut_paciente=rut_paciente,
            nombre_paciente=nombre_paciente,
            rut_medico=rut_medico,
            nombre_medico=nombre_medico,
            fecha_emision=fecha_emision,
            medicamentos=medicamentos,
            notas_prescriptor=notas,
            datos_adicionales=datos_adicionales or {}
        )
        return receta
    
    @staticmethod
    @transaction.atomic
    def aprobar_receta(receta_id, usuario_farmaceutico):
        """Aprueba una receta y registra farmacéutico."""
        receta = Receta.objects.get(id=receta_id)
        receta.validar_vigencia_automatica()
        
        if receta.estado == Receta.Estado.VENCIDA:
            raise ValueError("La receta está vencida y no puede ser aprobada.")
        
        receta.estado = Receta.Estado.APROBADA
        receta.fecha_aprobacion = timezone.now()
        receta.aprobado_por = usuario_farmaceutico
        receta.save()
        
        return receta
    
    @staticmethod
    @transaction.atomic
    def rechazar_receta(receta_id, razon_rechazo):
        """Rechaza una receta con motivo."""
        receta = Receta.objects.get(id=receta_id)
        receta.estado = Receta.Estado.RECHAZADA
        receta.razon_rechazo = razon_rechazo
        receta.save()
        
        return receta
    
    @staticmethod
    @transaction.atomic
    def dispensar_receta(receta_id):
        """Marca receta como dispensada."""
        receta = Receta.objects.get(id=receta_id)
        receta.validar_vigencia_automatica()
        
        if receta.estado == Receta.Estado.VENCIDA:
            raise ValueError("La receta está vencida y no puede ser dispensada.")
        
        if receta.estado != Receta.Estado.APROBADA:
            raise ValueError(f"La receta debe estar aprobada. Estado actual: {receta.estado}")
        
        receta.estado = Receta.Estado.DISPENSADA
        receta.fecha_dispensacion = timezone.now()
        receta.save()
        
        return receta
    
    @staticmethod
    def listar_recetas_vigentes():
        """Retorna recetas vigentes (< 30 días)."""
        from datetime import date
        fecha_limite = date.today() - timedelta(days=30)
        return Receta.objects.filter(
            fecha_emision__gte=fecha_limite,
            estado__in=[Receta.Estado.PENDIENTE, Receta.Estado.APROBADA]
        )
    
    @staticmethod
    def listar_recetas_vencidas():
        """Retorna recetas vencidas (> 30 días)."""
        from datetime import date
        fecha_limite = date.today() - timedelta(days=30)
        return Receta.objects.filter(
            fecha_emision__lt=fecha_limite,
            estado__in=[Receta.Estado.PENDIENTE, Receta.Estado.APROBADA]
        )


class RecetaRetenidaISPService:
    """Servicio para gestión de recetas retenidas ISP (medicamentos controlados)."""
    
    @staticmethod
    def _generar_hash_sha256(datos):
        """Genera hash SHA-256 de los datos."""
        datos_str = str(datos).encode('utf-8')
        return hashlib.sha256(datos_str).hexdigest()
    
    @staticmethod
    @transaction.atomic
    def registrar_receta_retenida(receta_id, numero_serie_carnet_paciente,
                                   numero_serie_carnet_medico, folio_isp,
                                   usuario_dispensador):
        """Registra receta retenida ISP con encadenamiento de hash."""
        receta = Receta.objects.get(id=receta_id)
        
        # Obtener último hash registrado
        ultima_retenida = RecetaRetenidaISP.objects.last()
        hash_anterior = ultima_retenida.hash_sha256 if ultima_retenida else ''
        
        # Generar hash actual
        datos_receta = {
            'receta_id': receta.id,
            'folio': receta.folio,
            'rut_paciente': receta.rut_paciente,
            'nombre_paciente': receta.nombre_paciente,
            'medicamentos': receta.medicamentos,
        }
        hash_actual = RecetaRetenidaISPService._generar_hash_sha256(datos_receta)
        
        receta_retenida = RecetaRetenidaISP.objects.create(
            receta=receta,
            numero_serie_carnet_paciente=numero_serie_carnet_paciente,
            numero_serie_carnet_medico=numero_serie_carnet_medico,
            folio_isp=folio_isp,
            dispensado_por=usuario_dispensador,
            datos_receta_jsonb=datos_receta,
            hash_sha256=hash_actual,
            hash_anterior=hash_anterior
        )
        
        return receta_retenida
    
    @staticmethod
    def validar_integridad(receta_retenida_id):
        """Valida integridad del encadenamiento de hash."""
        receta_retenida = RecetaRetenidaISP.objects.get(id=receta_retenida_id)
        
        hash_calculado = RecetaRetenidaISPService._generar_hash_sha256(
            receta_retenida.datos_receta_jsonb
        )
        
        return hash_calculado == receta_retenida.hash_sha256


class UnidosisAsistencialService:
    """Servicio para gestión de unidosis asistencial."""
    
    @staticmethod
    @transaction.atomic
    def crear_unidosis(folio, numero_serie_carnet_paciente, rut_paciente,
                       nombre_paciente, medicamentos, usuario_solicitante):
        """Crea una nueva solicitud de unidosis."""
        unidosis = UnidosisAsistencial.objects.create(
            folio=folio,
            numero_serie_carnet_paciente=numero_serie_carnet_paciente,
            rut_paciente=rut_paciente,
            nombre_paciente=nombre_paciente,
            medicamentos=medicamentos,
            solicitado_por=usuario_solicitante
        )
        return unidosis
    
    @staticmethod
    @transaction.atomic
    def preparar_unidosis(unidosis_id):
        """Marca unidosis como preparada."""
        unidosis = UnidosisAsistencial.objects.get(id=unidosis_id)
        
        if unidosis.estado != UnidosisAsistencial.Estado.SOLICITADA:
            raise ValueError(f"Unidosis debe estar solicitada. Estado: {unidosis.estado}")
        
        unidosis.estado = UnidosisAsistencial.Estado.PREPARADA
        unidosis.save()
        
        return unidosis
    
    @staticmethod
    @transaction.atomic
    def dispensar_unidosis(unidosis_id, usuario_dispensador):
        """Dispensa unidosis y registra dispensador."""
        unidosis = UnidosisAsistencial.objects.get(id=unidosis_id)
        
        if unidosis.estado != UnidosisAsistencial.Estado.PREPARADA:
            raise ValueError(f"Unidosis debe estar preparada. Estado: {unidosis.estado}")
        
        unidosis.estado = UnidosisAsistencial.Estado.DISPENSADA
        unidosis.dispensado_por = usuario_dispensador
        unidosis.fecha_dispensacion = timezone.now()
        unidosis.save()
        
        return unidosis
    
    @staticmethod
    @transaction.atomic
    def cancelar_unidosis(unidosis_id, observaciones=''):
        """Cancela una unidosis."""
        unidosis = UnidosisAsistencial.objects.get(id=unidosis_id)
        
        if unidosis.estado == UnidosisAsistencial.Estado.DISPENSADA:
            raise ValueError("No se puede cancelar una unidosis ya dispensada.")
        
        unidosis.estado = UnidosisAsistencial.Estado.CANCELADA
        unidosis.observaciones = observaciones
        unidosis.save()
        
        return unidosis
