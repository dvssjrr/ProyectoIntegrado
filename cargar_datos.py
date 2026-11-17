"""
Script para cargar datos de demostración realistas en Farmasur.
Medicamentos, vacunas, lotes con stock y recetas.
"""
import os, sys, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'farmacia_project.settings'
django.setup()

from datetime import date, timedelta
from django.utils import timezone
from farmasur.models.inventario.models import Laboratorio, Producto, Lote
from farmasur.models.recetas.models import Receta
from farmasur.models.ventas.models import ConvenioIsapre

hoy = date.today()

# ── LABORATORIOS ──────────────────────────────────────────────
labs_data = [
    ('Laboratorio Chile', 'Chile', '+56 2 2350 7000', 'ventas@labchile.cl'),
    ('Bagó Chile', 'Chile', '+56 2 2580 3000', 'contacto@bago.cl'),
    ('Pfizer Chile', 'Estados Unidos', '+56 2 2770 5800', 'info@pfizer.cl'),
    ('Sinovac Biotech', 'China', '+86 10 8289 5566', 'info@sinovac.com'),
    ('AstraZeneca Chile', 'Reino Unido', '+56 2 2350 1500', 'contacto@astrazeneca.cl'),
    ('Roche Chile', 'Suiza', '+56 2 2290 9000', 'info@roche.cl'),
    ('Saval', 'Chile', '+56 2 2750 7000', 'ventas@saval.cl'),
    ('Mintlab', 'Chile', '+56 2 2480 9000', 'contacto@mintlab.cl'),
    ('Andrómaco', 'Chile', '+56 2 2440 1000', 'info@andromaco.cl'),
    ('GlaxoSmithKline Chile', 'Reino Unido', '+56 2 2382 8000', 'info@gsk.cl'),
    ('Sanofi Chile', 'Francia', '+56 2 2423 7000', 'contacto@sanofi.cl'),
    ('MSD Chile (Merck)', 'Estados Unidos', '+56 2 2655 8000', 'info@msd.cl'),
    ('Abbott Chile', 'Estados Unidos', '+56 2 2421 1000', 'contacto@abbott.cl'),
]

laboratorios = {}
for nombre, pais, tel, email in labs_data:
    lab, _ = Laboratorio.objects.get_or_create(
        nombre=nombre,
        defaults={'pais': pais, 'telefono': tel, 'email': email}
    )
    laboratorios[nombre] = lab

print(f"✓ {len(laboratorios)} laboratorios creados")

# ── MEDICAMENTOS ──────────────────────────────────────────────
medicamentos_data = [
    # (SKU, nombre_comercial, principio_activo, presentación, categoría, laboratorio, condición_venta, precio, stock_min, cadena_frío)
    # --- Analgésicos ---
    ('7801234000010', 'Paracetamol 500mg', 'Paracetamol', '500mg comprimido x30', 'ANALGESICO', 'Laboratorio Chile', 'LIBRE', 2990, 20, False),
    ('7801234000027', 'Ibuprofeno 400mg', 'Ibuprofeno', '400mg comprimido x20', 'ANALGESICO', 'Mintlab', 'LIBRE', 3490, 15, False),
    ('7801234000034', 'Tapsin Día Noche', 'Paracetamol + Clorfeniramina', 'Cápsulas x18', 'ANALGESICO', 'Mintlab', 'LIBRE', 5990, 25, False),
    ('7801234000041', 'Kitadol Migra', 'Paracetamol + Cafeína', '500mg/65mg comp x10', 'ANALGESICO', 'Laboratorio Chile', 'LIBRE', 4290, 15, False),
    ('7801234000058', 'Tramadol 50mg', 'Tramadol clorhidrato', '50mg cápsula x20', 'CONTROLADO', 'Saval', 'RECETA_RETENIDA', 8990, 5, False),

    # --- Antiinflamatorios ---
    ('7801234000065', 'Diclofenaco 50mg', 'Diclofenaco sódico', '50mg comprimido x20', 'ANTIINFLAMATORIO', 'Bagó Chile', 'RECETA_SIMPLE', 3290, 15, False),
    ('7801234000072', 'Naproxeno 550mg', 'Naproxeno sódico', '550mg comprimido x10', 'ANTIINFLAMATORIO', 'Saval', 'RECETA_SIMPLE', 4590, 10, False),
    ('7801234000089', 'Meloxicam 15mg', 'Meloxicam', '15mg comprimido x10', 'ANTIINFLAMATORIO', 'Andrómaco', 'RECETA_SIMPLE', 5890, 10, False),

    # --- Antibióticos ---
    ('7801234000096', 'Amoxicilina 500mg', 'Amoxicilina', '500mg cápsula x21', 'ANTIBIOTICO', 'Laboratorio Chile', 'RECETA_SIMPLE', 4990, 10, False),
    ('7801234000102', 'Azitromicina 500mg', 'Azitromicina', '500mg comprimido x3', 'ANTIBIOTICO', 'Bagó Chile', 'RECETA_SIMPLE', 7890, 8, False),
    ('7801234000119', 'Ciprofloxacino 500mg', 'Ciprofloxacino', '500mg comprimido x14', 'ANTIBIOTICO', 'Saval', 'RECETA_SIMPLE', 9890, 8, False),
    ('7801234000126', 'Cefalexina 500mg', 'Cefalexina', '500mg cápsula x20', 'ANTIBIOTICO', 'Mintlab', 'RECETA_SIMPLE', 6490, 10, False),

    # --- Antihistamínicos ---
    ('7801234000133', 'Loratadina 10mg', 'Loratadina', '10mg comprimido x30', 'ANTIHISTAMINICO', 'Andrómaco', 'LIBRE', 3990, 15, False),
    ('7801234000140', 'Cetirizina 10mg', 'Cetirizina', '10mg comprimido x30', 'ANTIHISTAMINICO', 'Laboratorio Chile', 'LIBRE', 4290, 15, False),
    ('7801234000157', 'Clorfenamina 4mg', 'Clorfenamina maleato', '4mg comprimido x20', 'ANTIHISTAMINICO', 'Mintlab', 'LIBRE', 1990, 20, False),

    # --- Vitaminas ---
    ('7801234000164', 'Vitamina C 1000mg', 'Ácido ascórbico', '1000mg efervescente x10', 'VITAMINA', 'Roche Chile', 'LIBRE', 5490, 20, False),
    ('7801234000171', 'Vitamina D3 800UI', 'Colecalciferol', '800UI cápsula x30', 'VITAMINA', 'Abbott Chile', 'LIBRE', 7990, 10, False),
    ('7801234000188', 'Complejo B', 'Vitaminas B1+B6+B12', 'Comprimido x30', 'VITAMINA', 'Saval', 'LIBRE', 6290, 12, False),

    # --- Controlados ---
    ('7801234000195', 'Clonazepam 0.5mg', 'Clonazepam', '0.5mg comprimido x30', 'CONTROLADO', 'Laboratorio Chile', 'RECETA_RETENIDA', 4290, 5, False),
    ('7801234000201', 'Alprazolam 0.5mg', 'Alprazolam', '0.5mg comprimido x30', 'CONTROLADO', 'Bagó Chile', 'RECETA_RETENIDA', 5990, 5, False),
    ('7801234000218', 'Metilfenidato 10mg', 'Metilfenidato clorhidrato', '10mg comprimido x30', 'CONTROLADO', 'Saval', 'RECETA_RETENIDA', 12990, 3, False),
    ('7801234000225', 'Pregabalina 75mg', 'Pregabalina', '75mg cápsula x30', 'CONTROLADO', 'Pfizer Chile', 'RECETA_RETENIDA', 18990, 5, False),
    ('7801234000232', 'Codeína 30mg + Paracetamol', 'Codeína + Paracetamol', '30mg/500mg comp x20', 'CONTROLADO', 'Andrómaco', 'RECETA_RETENIDA', 7990, 5, False),

    # --- Otros medicamentos comunes ---
    ('7801234000249', 'Omeprazol 20mg', 'Omeprazol', '20mg cápsula x30', 'OTRO', 'Laboratorio Chile', 'RECETA_SIMPLE', 4990, 15, False),
    ('7801234000256', 'Losartán 50mg', 'Losartán potásico', '50mg comprimido x30', 'OTRO', 'Saval', 'RECETA_SIMPLE', 5490, 12, False),
    ('7801234000263', 'Metformina 850mg', 'Metformina clorhidrato', '850mg comprimido x30', 'OTRO', 'Andrómaco', 'RECETA_SIMPLE', 3990, 12, False),
    ('7801234000270', 'Atorvastatina 20mg', 'Atorvastatina', '20mg comprimido x30', 'OTRO', 'Pfizer Chile', 'RECETA_SIMPLE', 8990, 10, False),
    ('7801234000287', 'Enalapril 10mg', 'Enalapril maleato', '10mg comprimido x30', 'OTRO', 'Mintlab', 'RECETA_SIMPLE', 3290, 12, False),
    ('7801234000294', 'Levotiroxina 50mcg', 'Levotiroxina sódica', '50mcg comprimido x50', 'OTRO', 'Bagó Chile', 'RECETA_SIMPLE', 6990, 10, False),
    ('7801234000300', 'Salbutamol Inhalador', 'Salbutamol sulfato', '100mcg/dosis 200 dosis', 'OTRO', 'GlaxoSmithKline Chile', 'RECETA_SIMPLE', 7490, 8, False),

    # ── VACUNAS (requieren cadena de frío) ──
    ('7801234001017', 'Vacuna Influenza 2027', 'Virus influenza inactivado', 'Jeringa prellenada 0.5mL', 'OTRO', 'Sanofi Chile', 'RECETA_SIMPLE', 15990, 10, True),
    ('7801234001024', 'Vacuna COVID-19 Bivalente', 'ARNm SARS-CoV-2', 'Vial multidosis 5 dosis', 'OTRO', 'Pfizer Chile', 'RECETA_SIMPLE', 0, 5, True),
    ('7801234001031', 'Vacuna Hepatitis B', 'Antígeno superficie HB', 'Jeringa prellenada 1mL', 'OTRO', 'GlaxoSmithKline Chile', 'RECETA_SIMPLE', 18990, 5, True),
    ('7801234001048', 'Vacuna Neumocócica 13v', 'Polisacárido neumococo conjugado', 'Jeringa prellenada 0.5mL', 'OTRO', 'Pfizer Chile', 'RECETA_SIMPLE', 42990, 3, True),
    ('7801234001055', 'Vacuna DTPa (Boostrix)', 'Difteria+Tétanos+Pertussis', 'Jeringa prellenada 0.5mL', 'OTRO', 'GlaxoSmithKline Chile', 'RECETA_SIMPLE', 24990, 5, True),
    ('7801234001062', 'Vacuna HPV Gardasil 9', 'Papilomavirus tipos 6/11/16/18/31/33/45/52/58', 'Jeringa prellenada 0.5mL', 'OTRO', 'MSD Chile (Merck)', 'RECETA_SIMPLE', 89990, 3, True),
    ('7801234001079', 'Vacuna Herpes Zóster', 'Virus varicela-zóster recombinante', 'Vial + jeringa diluyente', 'OTRO', 'GlaxoSmithKline Chile', 'RECETA_SIMPLE', 125990, 2, True),
    ('7801234001086', 'Vacuna Fiebre Amarilla', 'Virus fiebre amarilla atenuado', 'Vial liofilizado 1 dosis', 'OTRO', 'Sanofi Chile', 'RECETA_SIMPLE', 35990, 3, True),
]

productos = {}
for sku, nombre, pa, pres, cat, lab_name, cond, precio, stock_min, frio in medicamentos_data:
    prod, _ = Producto.objects.get_or_create(
        sku_codigo_barra=sku,
        defaults={
            'nombre_comercial': nombre,
            'principio_activo': pa,
            'presentacion': pres,
            'categoria': cat,
            'laboratorio': laboratorios[lab_name],
            'condicion_venta': cond,
            'precio_clp': precio,
            'stock_minimo_vitrina': stock_min,
            'requiere_cadena_frio': frio,
        }
    )
    productos[sku] = prod

print(f"✓ {len(productos)} productos creados (medicamentos + vacunas)")

# ── LOTES CON STOCK ───────────────────────────────────────────
import random
random.seed(42)

lotes_creados = 0
for sku, prod in productos.items():
    num_lotes = random.randint(1, 3)
    for i in range(num_lotes):
        codigo = f"LT-{prod.id:03d}-{2026 + i}{random.randint(10,99)}"
        venc = hoy + timedelta(days=random.randint(45, 540))

        # Algunos lotes próximos a vencer
        if random.random() < 0.12:
            venc = hoy + timedelta(days=random.randint(5, 25))

        # Un par vencidos
        if random.random() < 0.05:
            venc = hoy - timedelta(days=random.randint(1, 30))

        stock_v = random.randint(3, 50)
        stock_b = random.randint(10, 120)
        costo = int(prod.precio_clp * random.uniform(0.45, 0.65))

        lote, created = Lote.objects.get_or_create(
            producto=prod,
            codigo_lote=codigo,
            defaults={
                'fecha_vencimiento': venc,
                'stock_vitrina': stock_v,
                'stock_bodega': stock_b,
                'costo_compra': costo,
                'bloqueado_vencimiento': venc < hoy,
            }
        )
        if created:
            lotes_creados += 1

print(f"✓ {lotes_creados} lotes creados con stock")

# ── RECETAS ───────────────────────────────────────────────────
recetas_data = [
    # (folio, rut_paciente, nombre_paciente, rut_médico, nombre_médico, fecha_emisión, estado, medicamentos, notas)
    ('REC-2026-0001', '187654321', 'María Isabel Contreras Soto', '123456789', 'Dr. Roberto Andrade M.', hoy - timedelta(days=2), 'APROBADA',
     [{'sku': '7801234000096', 'cantidad': 1, 'instrucciones': 'Tomar 1 cápsula cada 8 horas por 7 días'},
      {'sku': '7801234000065', 'cantidad': 1, 'instrucciones': 'Tomar 1 comprimido cada 12 horas con alimentos'}],
     'Infección respiratoria alta. Control en 7 días.'),

    ('REC-2026-0002', '165432187', 'Juan Carlos Muñoz Pérez', '134567890', 'Dra. Andrea Silva R.', hoy - timedelta(days=1), 'PENDIENTE',
     [{'sku': '7801234000195', 'cantidad': 1, 'instrucciones': 'Tomar 1 comprimido en la noche por 30 días'},],
     'Trastorno de ansiedad generalizada. Paciente en tratamiento.'),

    ('REC-2026-0003', '198765432', 'Ana Lucía Fernández Díaz', '145678901', 'Dr. Carlos Mendoza V.', hoy - timedelta(days=5), 'DISPENSADA',
     [{'sku': '7801234000249', 'cantidad': 1, 'instrucciones': 'Tomar 1 cápsula en ayunas por 30 días'},
      {'sku': '7801234000256', 'cantidad': 1, 'instrucciones': 'Tomar 1 comprimido cada 24 horas'}],
     'Hipertensión + reflujo gastroesofágico.'),

    ('REC-2026-0004', '176543210', 'Pedro Alejandro Rojas Vera', '156789012', 'Dra. Marcela Torres C.', hoy - timedelta(days=3), 'APROBADA',
     [{'sku': '7801234000102', 'cantidad': 1, 'instrucciones': 'Tomar 1 comprimido diario por 3 días'},],
     'Faringitis bacteriana aguda.'),

    ('REC-2026-0005', '154321098', 'Carmen Gloria Herrera Lagos', '167890123', 'Dr. Francisco Navarro P.', hoy - timedelta(days=10), 'DISPENSADA',
     [{'sku': '7801234000263', 'cantidad': 2, 'instrucciones': 'Tomar 1 comprimido con almuerzo y 1 con cena'},
      {'sku': '7801234000270', 'cantidad': 1, 'instrucciones': 'Tomar 1 comprimido en la noche'}],
     'Diabetes mellitus tipo 2 + dislipidemia. Control en 3 meses.'),

    ('REC-2026-0006', '209876543', 'Felipe Andrés Gutiérrez Pino', '178901234', 'Dra. Javiera Bravo S.', hoy, 'PENDIENTE',
     [{'sku': '7801234000225', 'cantidad': 1, 'instrucciones': 'Tomar 1 cápsula cada 12 horas por 30 días'},],
     'Dolor neuropático crónico. Derivar a neurólogo si no mejora.'),

    ('REC-2026-0007', '143210987', 'Sofía Valentina Reyes Muñoz', '189012345', 'Dr. Alejandro Cortés R.', hoy - timedelta(days=7), 'APROBADA',
     [{'sku': '7801234000119', 'cantidad': 1, 'instrucciones': 'Tomar 1 comprimido cada 12 horas por 10 días'},],
     'Infección urinaria. Urocultivo pendiente.'),

    ('REC-2026-0008', '132109876', 'Roberto Ernesto Vargas Cáceres', '190123456', 'Dra. Catalina Prado M.', hoy - timedelta(days=15), 'DISPENSADA',
     [{'sku': '7801234000201', 'cantidad': 1, 'instrucciones': 'Tomar 0.5mg en la noche por 30 días'},
      {'sku': '7801234000058', 'cantidad': 1, 'instrucciones': 'Tomar 1 cápsula cada 8 horas solo si dolor intenso'}],
     'Síndrome dolor crónico + insomnio. Reevaluar en 1 mes.'),

    ('REC-2026-0009', '210987654', 'Constanza Alejandra Morales Tapia', '201234567', 'Dr. Ignacio Fuentes L.', hoy - timedelta(days=4), 'APROBADA',
     [{'sku': '7801234000294', 'cantidad': 1, 'instrucciones': 'Tomar 1 comprimido en ayunas, 30 min antes del desayuno'},],
     'Hipotiroidismo subclínico. TSH 6.8. Control en 6 semanas.'),

    ('REC-2026-0010', '121098765', 'Héctor Damián Espinoza Ríos', '212345678', 'Dra. Paulina Araya G.', hoy - timedelta(days=35), 'VENCIDA',
     [{'sku': '7801234000096', 'cantidad': 1, 'instrucciones': 'Tomar 1 cápsula cada 8 horas por 7 días'},],
     'Infección dental. Receta vencida - no dispensar.'),

    # Recetas de vacunas
    ('REC-2026-0011', '198765000', 'Martina Paz González López', '223456789', 'Dr. Diego Salazar N.', hoy - timedelta(days=1), 'PENDIENTE',
     [{'sku': '7801234001017', 'cantidad': 1, 'instrucciones': 'Administrar 0.5mL IM en deltoides. Observar 30 min post-vacuna'}],
     'Vacunación influenza 2027. Paciente sin contraindicaciones.'),

    ('REC-2026-0012', '176543999', 'Daniela Ignacia Soto Arriagada', '234567890', 'Dra. Francisca Leal H.', hoy - timedelta(days=6), 'DISPENSADA',
     [{'sku': '7801234001062', 'cantidad': 1, 'instrucciones': 'Administrar 0.5mL IM. Segunda dosis en 2 meses'}],
     'HPV Gardasil 9. Primera dosis. Esquema 0-2-6 meses.'),

    ('REC-2026-0013', '154321555', 'Jorge Patricio Valdés Molina', '245678901', 'Dr. Matías Riquelme A.', hoy - timedelta(days=3), 'APROBADA',
     [{'sku': '7801234001031', 'cantidad': 1, 'instrucciones': 'Administrar 1mL IM en deltoides'},
      {'sku': '7801234001055', 'cantidad': 1, 'instrucciones': 'Administrar 0.5mL IM. Refuerzo cada 10 años'}],
     'Vacunación Hepatitis B + DTPa. Esquema laboral sector salud.'),

    ('REC-2026-0014', '187654888', 'Claudia Andrea Bustamante Parra', '256789012', 'Dra. Valentina Orrego C.', hoy, 'PENDIENTE',
     [{'sku': '7801234001048', 'cantidad': 1, 'instrucciones': 'Administrar 0.5mL IM. Paciente mayor 65 años'}],
     'Vacunación neumocócica. Adulto mayor con EPOC.'),

    ('REC-2026-0015', '165432777', 'Francisco Javier Paredes Urzúa', '267890123', 'Dr. Sebastián Cifuentes M.', hoy - timedelta(days=8), 'DISPENSADA',
     [{'sku': '7801234001086', 'cantidad': 1, 'instrucciones': 'Administrar subcutánea. Certificado internacional requerido'}],
     'Vacuna fiebre amarilla. Viaje a Brasil en 15 días.'),
]

recetas_creadas = 0
from farmasur.models.usuarios.models import Usuario
admin_user = Usuario.objects.filter(username='admin').first()

for folio, rut_pac, nom_pac, rut_med, nom_med, fecha_em, estado, meds, notas in recetas_data:
    receta, created = Receta.objects.get_or_create(
        folio=folio,
        defaults={
            'rut_paciente': rut_pac,
            'nombre_paciente': nom_pac,
            'rut_medico': rut_med,
            'nombre_medico': nom_med,
            'fecha_emision': fecha_em,
            'estado': estado,
            'medicamentos': meds,
            'notas_prescriptor': notas,
            'aprobado_por': admin_user if estado in ('APROBADA', 'DISPENSADA') else None,
            'fecha_aprobacion': timezone.now() if estado in ('APROBADA', 'DISPENSADA') else None,
            'fecha_dispensacion': timezone.now() if estado == 'DISPENSADA' else None,
        }
    )
    if created:
        recetas_creadas += 1

print(f"✓ {recetas_creadas} recetas creadas")

# ── CONVENIOS ISAPRE ──────────────────────────────────────────
convenios_data = [
    ('Fonasa', 'Fondo Nacional de Salud', 25, False),
    ('Consalud', 'Isapre Consalud', 30, False),
    ('Colmena Golden Cross', 'Isapre Colmena', 35, False),
    ('Cruz Blanca', 'Isapre Cruz Blanca', 28, False),
    ('Banmédica', 'Isapre Banmédica', 32, True),
    ('Vida Tres', 'Isapre Vida Tres', 27, False),
]

convenios_creados = 0
for nombre, desc, pct, req_qf in convenios_data:
    conv, created = ConvenioIsapre.objects.get_or_create(
        nombre=nombre,
        defaults={
            'descripcion': desc,
            'porcentaje_descuento': pct,
            'requiere_autorizacion_qf': req_qf,
        }
    )
    if created:
        convenios_creados += 1

print(f"✓ {convenios_creados} convenios Isapre creados")

# ── USUARIOS ADICIONALES ─────────────────────────────────────
usuarios_data = [
    ('mlopez', 'María López Castillo', '163456788', 'FARMACEUTICO', 'mlopez@farmasur.cl'),
    ('jperez', 'José Pérez Dinamarca', '174567891', 'TECNICO', 'jperez@farmasur.cl'),
    ('crodriguez', 'Camila Rodríguez Flores', '185678903', 'BODEGUERO', 'crodriguez@farmasur.cl'),
]

usuarios_creados = 0
for username, nombre, rut, rol, email in usuarios_data:
    if not Usuario.objects.filter(username=username).exists():
        u = Usuario(
            username=username,
            nombre_completo=nombre,
            rut=rut,
            rol=rol,
            email=email,
        )
        u.set_password('farmasur2026')
        u.save()
        usuarios_creados += 1

print(f"✓ {usuarios_creados} usuarios adicionales creados")

# ── RESUMEN ───────────────────────────────────────────────────
print("\n" + "="*50)
print("  DATOS DE DEMOSTRACIÓN CARGADOS EXITOSAMENTE")
print("="*50)
print(f"  Laboratorios:  {Laboratorio.objects.count()}")
print(f"  Productos:     {Producto.objects.count()}")
print(f"    → Medicamentos: {Producto.objects.exclude(requiere_cadena_frio=True).count()}")
print(f"    → Vacunas:      {Producto.objects.filter(requiere_cadena_frio=True).count()}")
print(f"  Lotes:         {Lote.objects.count()}")
print(f"  Recetas:       {Receta.objects.count()}")
print(f"  Convenios:     {ConvenioIsapre.objects.count()}")
print(f"  Usuarios:      {Usuario.objects.count()}")
print("="*50)
