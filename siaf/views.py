from sistema.models import Profile
from sistema.functions import generate_pdf

def enviarDeclaracionJurada(request):
    user = request.GET.get('a')


    template_name = 'registration/declaracion_jurada_pdf.html'
    profile = Profile.objects.get(user=user)
    context = {
        'profile': profile
    }

    return generate_pdf(request, template_name, context)
