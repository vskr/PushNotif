"""Python module for using the pushnotif API"""

#dependency
import requests
import base64
import json

from pushnotifconstants import *

#TODO USE TIME STAMP TO GENERATE AUTH_STRING 
#AND SINCE TIMESTAMPE KEEPS CHANGING, EVEN IF MALICIOUS USER
#KNOWS AUTH_STRING THAT WORKS ONLY FOR SOME TIME
#this is much better than having a static auth_string which has 1:1 mapping
#with secret , which is of no use, because if auth_string gets leaked, it is as
#bad as secret getting leaked too

def register_app(app_name, app_cert):
    """This registers your app with pushnotif service.

    This should be the first step to use pushnotif service
    Args
    app_name            str         App name
    app_cert            file object file object to ios cert file

    Return
    result              dict        {key:<app_key>, secret:<app_secret>} 
                                    throws exception on failure

    """
    params                  = {'app_name':app_name}
    files                   = {'app_cert':app_cert}
    add_result              = requests.post(ADD_APP_URL, params=params, files=files)

    if add_result.status_code == 201:
        return json.loads(add_result.text)
    else:
        raise Exception(add_result.text)

class Unauthorized(Exception):
    """Raised when we get a 401 from the server"""

class PushnotifFailure(Exception):
    """Raised when we get an error response from the server.

    args are (status code, message)

    """


class IdTypes:
    """Enum to classify a identifier, used to send push notifs,
    if id is a device token or an alias."""
    DEVICE_TOKEN    = 1
    ALIAS           = 2

class Pushnotif:

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

        self.auth_string = base64.b64encode('%s:%s' % (self.key, self.secret))
    
    def __repr__(self):
        return repr((self.key[:4] + '...', self.secret[:4] + '...'))

    def _request(self, method, body, url, content_type=None):
        ###TODO This is a very basic auth, and should be changed later
        ####TODO Better way to handle all kinds of http verbs
        headers = { 'Authorization' : self.key}
        if content_type:
            headers['content-type'] = content_type
        ##make the request
        r = requests.post(url, params=body,headers=headers)
        if r.status_code == 401:
            raise Unauthorized(r.status_code, "Request failed probably due to wrong API. Please check the API you are using")

        return r.status_code, r.text

    def register(self, device_token, alias_id=None, tag1=None, tag2=None, tag3=None, tag4=None, tag5=None, lat=None, lng=None):
        """Register the device token.

	Args
	device_token            str	        Device token of the device
	alias_id		str		An alias id for this device token. 
                                                This parameter is only for convenience,
                                                and it should be used if app developers
                                                find it easier to work with app-specific
                                                unique ids (e.g. logged-in user ids) 
                                                instead of device tokens
        tag1...tag5             str             Tags that are used to identify dev token/
                                                alias_id
        lat                     float           Latitude of this device/alias
        lng                     float           Longitude of this device/alias


	Return
	result			bool		Returns the result of registering the device token
						True if successful, false otherwise	
	"""
		
	
        url = DEVICE_TOKEN_REGISTER_URL
        payload = {}
	payload['device_token'] = device_token
	payload['tag1'] = tag1
	payload['tag2'] = tag2
	payload['tag3'] = tag3
	payload['tag4'] = tag4
	payload['tag5'] = tag5
	payload['lat']  = lat
	payload['lng']  = lng

        if alias_id is not None:
            payload['alias_id'] = alias_id
        #body = json.dumps(payload)
        content_type = 'application/json'

        status, response = self._request('POST', payload, url, content_type)
        if not status in (200, 201):
            raise PushnotifFailure(status, response)
        return status == 201

    def deregister_device(self, device_token):
        """De-registers device associated with this device token.

        You cannot send pushnotifs to a device, after deregistering, until you
        register the device again.

        Args
        device_token            str             Device token of the device
        """
        payload = {'dev_token' : device_token}
        status, response = \
                self._request('POST', payload, DEREGISTER_DEVICE_URL, None)
        if not status in (200, 201):
            raise PushnotifFailure(status, response)
        return status == 201

    def deregister_alias(self, alias):
        """De-registers all the devices associated with this device token.

        You cannont send push notifs to this alias, and therefor any devices
        associated to that alias after de-registering that alias.

        Args
        alias                   str             Alias-id of the user,whose devices
                                                will be de-registered
        """
        payload = {'alias_id' : alias}
        status, response = self._request('POST', payload, DEREGISTER_ALIAS_URL, None)
        if not status in (200, 201):
            raise PushnotifFailure(status, response)
        return status == 201

    def push_to_device(self, payload, device_token):
        """Sends a push notif to device associated with device_token."""
        #TODO Define structure around payload
        data= {}
        data['payload'] = payload
        data['device_token'] = device_token 
        status, response = self._request('POST', data, PUSH_TO_DEVICE_URL, 'application/json')
        if not status == 200:
            raise PushnotifFailure(status, response)
        return status == 200

    def push_to_alias(self, payload, *aliases):
        """Pushes payload to all the devices associated with alias."""
        data= {}
        data['payload'] = payload
        data['aliases'] = aliases
        status, response = self._request('POST', data, PUSH_TO_ALIAS_URL, 'application/json')
        if not status == 200:
            raise PushnotifFailure(status, response)
        return status == 200


    def broadcast(self, payload):
        """Broadcast this payload to all users."""
        #body = json.dumps(payload)
        status, response = self._request('POST', {'payload':payload}, BROADCAST_URL,
            'application/json')
        if not status == 200:
            raise PushnotifFailure(status, response)
        return (status == 200) or (status == 201)

    def add_geotag_to_alias(self, lat, lng, alias):
        """Adds location tag to given device tokens and alias ids.

        Args
        lat                 float           Latitude of the reference point
        lng                 float           Longitude of the reference point
        device_tokens       list            List of device tokens which should be tagged with given location
        alias_ids           list            List of alias_ids which should be tagged with given location

        Main reason this function accepts device_tokens or alias_ids is because sometimes apps find it easier to 
        deal with alias_ids instead of device tokens. This function also takes device tokens, if app doesn't maintain
        any alias_ids(unique ids)


        Return
        result              bool            True on success, false otherwise

        """
#        payload = {}
#        payload['lat'] = lat
#        payload['lng'] = lng
#
#        payload['alias'] = alias
#        status, response = self._request('POST', payload, GEO_TAG_URL, 'application/json')
#        if not status == 200:
#            raise PushnotifFailure(status, response)
        return self._add_tag_helper(alias, IdTypes.ALIAS, lat=lat, lng=lng)

    def add_geotag_to_device(self, lat, lng, dev_token):
        """Adds location tag to given device tokens and alias ids.

        Args
        lat                 float           Latitude of the reference point
        lng                 float           Longitude of the reference point
        device_token        str             device token to tag geo info

        Main reason this function accepts device_tokens or alias_ids is because sometimes apps find it easier to 
        deal with alias_ids instead of device tokens. This function also takes device tokens, if app doesn't maintain
        any alias_ids(unique ids)


        Return
        result              bool            True on success, false otherwise

        """
#        payload = {}
#        payload['lat'] = lat
#        payload['lng'] = lng
#
#        payload['alias'] = alias
#        status, response = self._request('POST', payload, GEO_TAG_URL, 'application/json')
#        if not status == 200:
#            raise PushnotifFailure(status, response)
        return self._add_tag_helper(dev_token, IdTypes.DEVICE_TOKEN, lat=lat, lng=lng)

    def push_by_geo(self,lat,lng, radius, payload, alias_id):
        """Broadcasts push notif to aliases or devices within a given radius of location.

        Args
        lat                 float           Latitude of the reference point
        lng                 float           Longitude of the reference point
        radius              int             Radius around the above location, to broadcast the 
                                            push notifs
        TODO Formalize the payload
        payload             string          pn payload
        """
        #m_payload = {}
        #m_payload['lat'] = lat
        #m_payload['lng'] = lng
        #m_payload['radius'] = radius
        #m_payload['payload'] = payload
        #m_payload['alias_id'] = alias_id
        ##body = json.dumps(m_payload)
        #status, response = self._request('POST', m_payload, GEO_BROADCAST_URL, 'application/json')
        #if not status == 200:
        #    raise PushnotifFailure(status, response)
        self.push_by_tag(alias_id, payload, lat=lat, lng=lng, radius=radius)

    def push_by_tag(self, user_id, payload, tag1=None, tag2=None, tag3=None, tag4=None, tag5=None, lat=None, lng=None, radius=0):
        """Sends push notif to users who match all the given tags.

        Args
        user_id             int             Unique id of the user who is sending the push notification
        payload             string          Payload/String of the push notification message
        tag1...tag5         string          Tags that are used to filter users
        lat                 float           Latitude of the reference point
        lng                 float           Longitude of the reference point
        radius              int             Radius of the bounding circle, with (lat,lng) as the center
                                            used for filtering users
        """
        m_payload = {}
        m_payload['user_id'] = user_id
        m_payload['payload'] = payload

        m_payload['tag1'] = tag1 
        m_payload['tag2'] = tag2 
        m_payload['tag3'] = tag3 
        m_payload['tag4'] = tag4 
        m_payload['tag5'] = tag5 

        m_payload['lat'] = lat 
        m_payload['lng'] = lng
        m_payload['radius'] = radius 

        #body = json.dumps(m_payload)
        status, response = self._request('POST', m_payload, PUSH_BY_TAG_URL, 'application/json')
        if not status == 200:
            raise PushnotifFailure(status, response)

        
    def add_tag_to_device(self, device_token, tag1=None, tag2=None, tag3=None, tag4=None, tag5=None, lat=None, lng=None):
        return self._add_tag_helper(device_token, IdTypes.DEVICE_TOKEN, tag1, tag2, tag3, tag4, tag5, lat, lng)

    def add_tag_to_alias(self, alias, tag1=None, tag2=None, tag3=None, tag4=None, tag5=None, lat=None, lng=None):
        return self._add_tag_helper(alias, IdTypes.ALIAS, tag1, tag2, tag3, tag4, tag5, lat, lng)

    def _add_tag_helper(self, identifier, id_type, tag1=None, tag2=None, tag3=None, tag4=None, tag5=None, lat=None, lng=None):
        """Adds or updates existing tags for given device_tokens or aliases.
        
        Args
        identifier          str             A unique identifier, alias or device token, that is used to 
                                            send push notifications
        id_type             IdTypes         One of IdTypes, DEVICE_TOKEN or ALIAS

        tag1                string          None means tag1 for above device_tokens/aliases will remain
                                            unchanged. Any value other than None means tag1 for above 
                                            device tokens and aliases will be updated
                                            to
        tag2                string          None means tag2 for above device_tokens/aliases will remain
                                            unchanged. Any value other than None means tag2 for above 
                                            device tokens and aliases will be updated
        
        tag3                string          None means tag3 for above device_tokens/aliases will remain
                                            unchanged. Any value other than None means tag3 for above 
                                            device tokens and aliases will be updated
        
        tag4                string          None means tag4 for above device_tokens/aliases will remain
                                            unchanged. Any value other than None means tag4 for above 
                                            device tokens and aliases will be updated

        tag5                string          None means tag5 for above device_tokens/aliases will remain
                                            unchanged. Any value other than None means tag5 for above 
                                            device tokens and aliases will be updated

        Return
        result              bool            True on success, false otherwise
        """
        #e.g. if client wants to udpate only tag2 and tag4, function call would look like the following
        #addTag(dev_token,alias,tag2="newtag2", tag4="newtag4"). Python's named arguments helps in avoiding
        #including default values for other tags in function call
        payload = {}
        if id_type == IdTypes.DEVICE_TOKEN:
            payload['device_token'] = identifier
            url                     = ADD_TAG_TO_DEVICE_URL
        elif id_type == IdTypes.ALIAS:
            payload['alias']        = identifier
            url                     = ADD_TAG_TO_ALIAS_URL
        else:
            raise Exception("Wrong Id Type, should be either IdTypes.DEVICE_TOKEN or IdTypes.ALIAS")

        if tag1 is not None:
            payload['tag1']      = tag1
        if tag2 is not None:
            payload['tag2']      = tag2
        if tag3 is not None:
            payload['tag3']      = tag3
        if tag4 is not None:
            payload['tag4']      = tag4
        if tag5 is not None:
            payload['tag5']      = tag5

        if (lat is not None) and (lng is not None):
            payload['lat']       = lat
            payload['lng']       = lng


        #body = json.dumps(payload)
        status, response = self._request('POST', payload, url, 'application/json')
        if not status == 200:
            raise PushnotifFailure(status, response)

#########TODO Better api... separate dev_token and alias apis
#TODO addTagToAlias addTagtoDevtoken
#TODO addGeoTagToDevToken
#TODO allow them to send custom arguments
##This is part of defining payload structure
