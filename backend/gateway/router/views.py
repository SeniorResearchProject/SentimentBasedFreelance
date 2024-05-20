from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

class ProxyAPIView(APIView):
    def get(self, request, path):
        return self.forward_request('GET', path, request, params=request.query_params)

    def post(self, request, path):
        return self.forward_request('POST', path, request, json=request.data)

    def put(self, request, path):
        return self.forward_request('PUT', path, request, json=request.data)

    def delete(self, request, path):
        return self.forward_request('DELETE', path, request)

    def forward_request(self, method, path, request, *args, **kwargs):
        # Extracting the base URL and adjusting the path
        segments = path.split('/')
        service = segments[0]
        actual_path = '/'.join(segments[1:])  # Re-join the path without the service prefix

        base_url = self.get_microservice_base_url(service)
        if not base_url:
            return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the Authorization header is forwarded if it exists
        headers = kwargs.get('headers', {})
        if 'Authorization' in request.headers:
            headers['Authorization'] = request.headers['Authorization']
        kwargs['headers'] = headers

        # Construct the full URL to forward the request to
        full_url = f'{base_url}{actual_path}'
        response = requests.request(method, full_url, *args, **kwargs)
        if response.status_code == 200:
            return Response(response.json(), status=response.status_code)
        else:
            return Response(response.text, status=response.status_code)

    def get_microservice_base_url(self, service):
        # Mapping initial path segments to their respective microservices
        if service == 'user':
            return 'http://localhost:8000/'
        elif service == 'employer':
            return 'http://localhost:8001/'
        elif service == 'freelancer':
            return 'http://localhost:8002/'
        elif service == 'sentiment':
            return 'http://localhost:8003/'
        elif service == 'payment':
            return 'http://localhost:8004/'
        return None
