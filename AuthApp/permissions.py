from rest_framework import permissions
from rest_framework import exceptions

from rest_framework_api_key.models import APIKey

def get_authorization_header( request):

    auth = request.headers.get('Authorization')
    return auth


# Custom Permissions for HasAPIKey and Passed as headers : Authorization
class HasAPIKeyPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        # Check token is send or not
        auth = get_authorization_header(request).split() if get_authorization_header(request) else  None

        if auth is None or len(auth) == 1 :
            raise exceptions.AuthenticationFailed(
                "Invalid basic header. No credentials provided.")

        # To check if Authorization is valid
        if len(auth) > 2 :
            raise exceptions.AuthenticationFailed(
                "Invalid basic header. Credential string is not properly formatted")

        #  Token should be with Bearer
        if not auth or auth[0].lower() != "api-key":
            return None

        # Check if APIKey exists
        try:
            if not APIKey.objects.get_from_key(auth[1]):
                return None
        except Exception as e:
            return None

        return True
