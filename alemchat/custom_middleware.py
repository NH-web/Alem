from user_agents import parse

class MobileDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(user_agent_string)

        # Set a flag on the request based on the client type
        request.is_mobile = user_agent.is_mobile

        response = self.get_response(request)
        return response