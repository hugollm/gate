import json

from .endpoint import Endpoint
from ..requests.json_request import JsonRequest
from ..responses.json_response import JsonResponse


class JsonEndpoint(Endpoint):

    def _make_response(self):
        return JsonResponse()

    def handle_request(self, request):
        request = JsonRequest(request.env)
        response = super(JsonEndpoint, self).handle_request(request)
        response.body = json.dumps(response.json)
        return response
