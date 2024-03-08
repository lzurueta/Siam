from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('proveedoresHome', login_required(views.proveedoresHome.as_view()), name="proveedoresHome"),
    path('op_pagadas', login_required(views.op_pagadas.as_view()), name="op_pagadas"),
    path('op_pagadas_detalle', login_required(views.op_pagadas_detalle), name="op_pagadas_detalle"),
    path('op_pagadas_comprobante', login_required(views.op_pagadas_comprobante), name="op_pagadas_comprobante"),
    path('op_pagadas_imprimir/<int:OpaAnio>/<int:OpaNro>/<str:jurcod>/<str:repudo>', login_required(views.op_pagadas_imprimir.as_view()), name="op_pagadas_imprimir"),
    path('op_pagadas_ajax', login_required(views.op_pagadas_ajax), name="op_pagadas_ajax"),
]
