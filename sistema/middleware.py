from django.shortcuts import render

class NotFoundMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404 or response.status_code == 500 or response.status_code == 403:
            return render(request, '403.html', {'error': response.status_code}   )
        return response