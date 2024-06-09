from django.utils.deprecation import MiddlewareMixin

class CorsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response["Access-Control-Allow-Origin"] = "*"  # Allow requests from any origin
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"  # Allow specific HTTP methods
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"  # Allow specific headers
        return response
