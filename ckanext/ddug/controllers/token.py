"""
The default implementation of the OAuth provider includes two public endpoints
that are meant for client (as defined in :rfc:`1`) interaction.
.. attribute:: ^authorize/$
    This is the URL where a client should redirect a user to for authorization.
    This endpoint expects the parameters defined in :rfc:`4.1.1` and returns
    responses as defined in :rfc:`4.1.2` and :rfc:`4.1.2.1`.
.. attribute:: ^access_token/$
    This is the URL where a client exchanges a grant for an access tokens.
    This endpoint expects different parameters depending on the grant type:
    * Access tokens: :rfc:`4.1.3`
    * Refresh tokens: :rfc:`6`
    * Password grant: :rfc:`4.3.2`
    This endpoint returns responses depending on the grant type:
    * Access tokens: :rfc:`4.1.4` and :rfc:`5.1`
    * Refresh tokens: :rfc:`4.1.4` and :rfc:`5.1`
    * Password grant: :rfc:`5.1`
    Errors are outlined in :rfc:`5.2`.
"""
import json

import logging
log = logging.getLogger(__name__)

from pylons import session, config, request, response

from ckan import model
from ckan.plugins import toolkit as tk


from ckanext.oauth2provider.model.client import Client
from ckanext.oauth2provider.model.grant import Grant
#from ckanext.oauth2provider.model.access_token import AccessToken
from ckanext.oauth2provider.utils import set_query_parameter, get_token_expiry

#c = tk.c
from ckanext.oauth2provider.controllers.token import OAuth2ProviderTokenController 

class DdugTokenController(OAuth2ProviderTokenController):


    def authorize(self):
        context = self._get_context()
        auto_allow_addresses = config.get('ckanext.ddug.auto_allow_remote_addresses',
                                          '127.0.0.1') 
        address_list = auto_allow_addresses.split() 
        remote_address = request.remote_addr
         
        try:
            tk.check_access('oauth2provider_token_create', context)
        except tk.NotAuthorized:
            return tk.abort(401)

        client_id = self._get_required_param('client_id')
        response_type = tk.request.params.get('redirect_uri', 'code')

        redirect_uri = tk.request.params.get('redirect_uri', '')
        state = tk.request.params.get('state', '')

        convert_user_name_or_id_to_id = tk.get_converter(
            'convert_user_name_or_id_to_id')
        user_id = convert_user_name_or_id_to_id(context['user'], context)

        # If the grant already exists.
        grant = Grant.get(user_id=user_id, client_id=client_id)
        if grant:
            if state:
                redirect_uri = set_query_parameter(redirect_uri, 'state', state)
            # Send the grant code to client via GET as defined by OAuth spec
            redirect_uri = set_query_parameter(redirect_uri, 'code', grant.code)

            return tk.redirect_to(str(redirect_uri))
        # if remote address is in auto allow list
        elif(remote_address in address_list):
            client = Client.get(client_id=client_id)
            scope = 'read'
    
            grant = tk.get_action('oauth2provider_grant_create')(context, {
                'client_id': client.client_id,
                'user_id': user_id,
                'redirect_uri': redirect_uri,
                'scope': scope,
            })
    
            if state:
                redirect_uri = set_query_parameter(redirect_uri, 'state', state)
    
            # Send the grant code to client via GET as defined by OAuth spec
            redirect_uri = set_query_parameter(redirect_uri, 'code', grant.code)
    
            return tk.redirect_to(str(redirect_uri))            
        else: 
            if state:
                session['oauth2provider_state'] = state
                session.save()
    
            client = Client.get(client_id=client_id)
            scope = self._get_required_param('scope').split(' ')
    
            data = {
                'client_name': client.name,
                'client_id': client.client_id,
                'response_type': response_type,
                'redirect_uri': redirect_uri,
                'scopes': scope,
            }
    
            vars = {'data': data, 'action': 'authorize'}
            return tk.render('ckanext/oauth2provider/authorize.html',
                extra_vars=vars)


