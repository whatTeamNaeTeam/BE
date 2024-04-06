from django.utils.deprecation import MiddlewareMixin


class AttachJWTFromHeaderToCookieMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.APIS = ['github/login', 'github/finish', 'token/refresh']
    
    def process_response(self, request, response):
        path = request.path_info
        is_valid = any(api in path for api in self.APIS)

        if is_valid:
            if request.META.get('HTTP_FROM', None) == 'web':
                response.set_cookie('refresh', response.data['refresh'])
                response.set_cookie('access', response.data['access'])
                
                response.data.pop('access')
                response.data.pop('refresh')

                response.content = response.render().rendered_content
        
        return response
