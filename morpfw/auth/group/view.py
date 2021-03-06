from ..app import App
from .model import GroupCollection, GroupModel
from .model import GroupSchema, MemberSchema
from ..validator import validate
from ..utils import rellink
from morpfw.util import get_user
from morpfw.crud import permission
from morpfw.crud.errors import UnprocessableError
from morpfw.crud.validator import validate_schema, get_data
from webob.exc import HTTPNotFound, HTTPForbidden, HTTPInternalServerError


@App.json(model=GroupModel,
          name='members',
          permission=permission.View)
def list_members(context, request):
    """Return the list of users in the group."""
    members = context.members()
    return {
        'users': [{
            'username': m.identifier,
            'roles': context.get_member_roles(m.identifier),
            'links': [rellink(m, request)]
        } for m in members]
    }


@App.json(model=GroupModel, name='grant', request_method='POST',
          permission=permission.Edit)
def grant_member(context, request):
    """Grant member roles in the group."""
    mapping = request.json['mapping']
    for username, roles in mapping.items():
        for rolename in roles:
            # check if user exists
            user = get_user(request, username)
            if user is None:
                raise UnprocessableError('User %s does not exists' % username)
            context.grant_member_role(username, rolename)
    return {'status': 'success'}


@App.json(model=GroupModel, name='revoke', request_method='POST',
          permission=permission.Edit)
def revoke_member(context, request):
    """Revoke member roles in the group."""
    mapping = request.json['mapping']
    for username, roles in mapping.items():
        for rolename in roles:
            context.revoke_member_role(username, rolename)
    return {'status': 'success'}
