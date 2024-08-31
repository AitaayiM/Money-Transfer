from rest_framework.response import Response
from rest_framework import status

def role_required(*roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.roles.filter(name__in=roles).exists():
                return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
