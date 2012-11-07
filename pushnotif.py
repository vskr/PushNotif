"""Python module for using the pushnotif API"""

import httplib
#dependency
import requests
import base64
try:
    import json
except ImportError:
    import simplejson as json

from pushnotifconstants import *

#TODO USE TIME STAMP TO GENERATE AUTH_STRING 
#AND SINCE TIMESTAMPE KEEPS CHANGING, EVEN IF MALICIOUS USER
#KNOWS AUTH_STRING THAT WORKS ONLY FOR SOME TIME
#this is much better than having a static auth_string which has 1:1 mapping
#with secret , which is of no use, because if auth_string gets leaked, it is as
#bad as secret getting leaked too
class Unauthorized(Exception):
    """Raised when we get a 401 from the server"""


class PushnotifFailure(Exception):
    """Raised when we get an error response from the server.

    args are (status code, message)

    """

class Pushnotif:

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

        self.auth_string = base64.b64encode('%s:%s' % (self.key, self.secret))
        ##TODO Remove this
    def _request2(self, method, body, url, content_type=None):
	#TODO Support https
        #h = httplib.HTTPSConnection(SERVER)
        h = httplib.HTTPConnection(SERVER)
        headers = {
            'Authorization': 'Basic %s' % self.auth_string,
        }
        if content_type:
            headers['content-type'] = content_type
        h.request(method, url, body=body, headers=headers)
        resp = h.getresponse()
        if resp.status == 401:
            raise Unauthorized(resp.status, "Request failed probably due to wrong combination of api key and secret. Please check the key and secret you are using")

        return resp.status, resp.read()

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

    def register(self, device_token, alias_id=None):
        #TODO Allow users to add tags while registering
        """Register the device token.

        TODO Add support for adding tags on register time
	Args
	TODO Include data types too	
	device_token		-		Device token of the device
	alias_id		str		An alias id for this device token.
						This parameter is only for convenience, and it should be used if app 
						developers find it easier to work with app-specific unique ids 
						(e.g. logged-in user ids) instead of device tokens
        TODO Add tags info
        Make it a fixed number of tags

	Return
	TODO Improve the return value
	result			bool		Returns the result of registering the device token
						True if successful, false otherwise	
	"""
		
	
        url = DEVICE_TOKEN_REGISTER_URL
        payload = {}
	payload['device_token'] = device_token
        if alias_id is not None:
            payload['alias_id'] = alias_id
        #body = json.dumps(payload)
        content_type = 'application/json'

        status, response = self._request('POST', payload, url, content_type)
        if not status in (200, 201):
            raise PushnotifFailure(status, response)
        return status == 201

    def deregister(self, device_token):
        """Mark this device token as inactive"""
        url = DEVICE_TOKEN_URL + device_token
        status, response = self._request('DELETE', '', url, None)
        if status != 204:
            raise PushnotifFailure(status, response)


    def pushToDevice(self, payload, device_token):
        """Pushes payload to the device token."""
        data= {}
        data['payload'] = payload
        data['device_token'] = device_token 
        status, response = self._request('POST', data, PUSH_TO_DEVICE_URL, 'application/json')
        if not status == 200:
            raise PushnotifFailure(status, response)

    def pushToAlias(self, payload, *aliases):
        """Pushes payload to all the devices associated with alias."""
        data= {}
        data['payload'] = payload
        data['aliases'] = aliases
        status, response = self._request('POST', data, PUSH_TO_ALIAS_URL, 'application/json')
        if not status == 200:
            raise PushnotifFailure(status, response)


    def broadcast(self, payload):
        """Broadcast this payload to all users."""
        #body = json.dumps(payload)
        status, response = self._request('POST', {'payload':payload}, BROADCAST_URL,
            'application/json')
        if not status == 200:
            raise PushnotifFailure(status, response)

    def addGeoTagToAlias(self, lat, lng, alias):
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
        payload = {}
        payload['lat'] = lat
        payload['lng'] = lng

        payload['alias'] = alias
        status, response = self._request('POST', payload, GEO_TAG_URL, 'application/json')
        if not status == 200:
            raise PushnotifFailure(status, response)

    def pushByGeo(self,lat,lng, radius, payload):
        """Broadcasts push notif to aliases or devices within a given radius of location.

        Args
        lat                 float           Latitude of the reference point
        lng                 float           Longitude of the reference point
        radius              int             Radius around the above location, to broadcast the 
                                            push notifs
        TODO Formalize the payload
        payload             string          pn payload
        """
        m_payload = {}
        m_payload['lat'] = lat
        m_payload['lng'] = lng
        m_payload['radius'] = radius
        m_payload['payload'] = payload
        #body = json.dumps(m_payload)
        status, response = self._request('POST', m_payload, GEO_BROADCAST_URL, 'application/json')
        if not status == 200:
            raise PushnotifFailure(status, response)

    def pushByTag(self, user_id, payload, tag1=None, tag2=None, tag3=None, tag4=None, tag5=None, lat=None, lng=None, radius=0):
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
        
    def addTagToAlias(self, alias, tag1=None, tag2=None, tag3=None, tag4=None, tag5=None, lat=None, lng=None):
        """Adds or updates existing tags for given device_tokens and aliases.
        
        Args
        device_tokens       list            List of device tokens whose tags will be updated/new tags
                                            will be added
        aliases             list            List of aliases whose tags will be updated/new tags will be 
                                            added
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
        payload['alias']       = alias

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
        status, response = self._request('POST', payload, ADD_TAG_URL, 'application/json')
        if not status == 200:
            raise PushnotifFailure(status, response)



###TODO Differentiate between
#simple send -> send to alias/dev tokens
#This is done by pushByTag and pushByAlias

#geo send, and/OR tag send -> send to everyone in this radius and/or who match some tags
###TODO Remove references to Pushnotif

#########TODO Better api... separate dev_token and alias apis
#TODO addTagToAlias addTagtoDevtoken
