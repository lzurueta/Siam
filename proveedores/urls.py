from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('', login_required(views.proveedoresHome.as_view()), name="proveedoresHome"),
    path('op_pagadas', login_required(views.op_pagadas.as_view()), name="op_pagadas"),
    path('op_pagadas_retenciones', login_required(views.op_pagadas_retenciones), name="op_pagadas_retenciones"),
    path('op_detalle', login_required(views.op_detalle), name="op_detalle"),
    path('op_pagadas_comprobante', login_required(views.op_pagadas_comprobante), name="op_pagadas_comprobante"),
    path('op_imprimir', login_required(views.op_imprimir), name="op_imprimir"),
    path('op_pagadas_ajax', login_required(views.op_pagadas_ajax), name="op_pagadas_ajax"),
    path('op_pagadas_excel', login_required(views.op_pagadas_excel), name="op_pagadas_excel"),

    path('datos_proveedor', login_required(views.datos_proveedor), name="datos_proveedor"),
    path('declaracion_jurada',login_required(views.datos_declaracion_jurada_imprimir), name="declaracion_jurada"),

    path('op_impagas', login_required(views.op_impagas.as_view()), name="op_impagas"),
    path('op_impagas_ajax', login_required(views.op_impagas_ajax), name="op_impagas_ajax"),
    path('op_impagas_excel', login_required(views.op_impagas_excel), name="op_impagas_excel"),

    path('op_comprobantes', login_required(views.op_comprobantes.as_view()), name="op_comprobantes"),
    path('op_comprobantes_ajax', login_required(views.op_comprobantes_ajax), name="op_comprobantes_ajax"),

    path('op_retenciones', login_required(views.op_retenciones.as_view()), name="op_retenciones"),
    path('op_retenciones_ajax', login_required(views.op_retenciones_ajax), name="op_retenciones_ajax"),
    path('op_retenciones_pdf', login_required(views.op_retenciones_pdf), name="op_retenciones_pdf"),
    path('op_retenciones_excel', login_required(views.op_retenciones_excel), name="op_retenciones_excel"),

    path('consultar_estado', login_required(views.consultar_estado), name='consultar_estado'),

    path('historial_pagos', login_required(views.historial_pagos.as_view()), name="historial_pagos"),
]
