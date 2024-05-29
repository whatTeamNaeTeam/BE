from .exceptions import IsNotOwnerError


class BaseService:
    def __init__(self, request, **kwargs):
        self.request = request
        self.kwargs = kwargs


class BaseServiceWithCheckOwnership(BaseService):
    def check_ownership(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id

        if owner_id != user_id:
            raise IsNotOwnerError()
