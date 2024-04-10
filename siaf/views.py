from sistema.models import Profile
from sistema.functions import generate_pdf
from django.contrib.auth.models import User

def enviarDeclaracionJurada(request):

    template_name = 'registration/declaracion_jurada_pdf.html'

    user = User.objects.get(id=request.GET.get('a'))
    profile = Profile.objects.get(user=user)



    context = {
        'profile': profile,
        'user': user
    }

    return generate_pdf(request, template_name, context)
