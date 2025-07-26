from django.utils.deprecation import MiddlewareMixin

class CustomXFrameOptionsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if '/media/' in request.path:
            response['X-Frame-Options'] = 'SAMEORIGIN'  # or another suitable setting
        return response
