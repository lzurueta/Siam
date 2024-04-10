from sistema.models import Profile
from sistema.functions import generate_pdf
from django.contrib.auth.models import User

import base64
def enviarDeclaracionJurada(request):

    template_name = 'registration/declaracion_jurada_pdf.html'

    id = str(request.GET.get('a'))
    encode = base64.b64decode(id.encode('utf-8'))
    a = encode.decode('utf-8')

    user = User.objects.get(id=a)
    profile = Profile.objects.get(user=user)

    context = {
        'profile': profile,
        'user': user
    }

    return generate_pdf(request, template_name, context)
