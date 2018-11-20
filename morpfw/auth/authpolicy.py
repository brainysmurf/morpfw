from more.jwtauth import JWTIdentityPolicy
from more.basicauth import BasicAuthIdentityPolicy
from morepath import Identity, NO_IDENTITY
from .path import get_apikey_collection
import rulez


class JWTWithAPIKeyIdentityPolicy(JWTIdentityPolicy):

    def identify(self, request):
        api_key = request.headers.get('X-API-KEY', None)
        if api_key:
            api_identity, api_secret = api_key.split('.')
            apikeys = get_apikey_collection(request)
            keys = apikeys.search(
                rulez.field['api_identity'] == api_identity, secure=False)
            if keys and keys[0].data['api_secret'] == api_secret:
                username = keys[0].data['username']
                return Identity(userid=username)
        return super(JWTWithAPIKeyIdentityPolicy, self).identify(request)
