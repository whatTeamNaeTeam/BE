class BaseService:
    def __init__(self, request, **kwargs):
        self.request = request
        self.kwargs = kwargs
