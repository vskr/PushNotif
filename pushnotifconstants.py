SERVER = 'localhost:8888'
#TODO Add https support
BASE_URL = "http://" + SERVER
DEVICE_TOKEN_URL = BASE_URL + '/device_tokens'
DEVICE_TOKEN_REGISTER_URL=DEVICE_TOKEN_URL  + '/register'
GEO_TAG_URL = BASE_URL + '/geo_tag'
GEO_BROADCAST_URL = BASE_URL + '/geo_broadcast' 

PUSH_BY_TAG_URL = BASE_URL + '/push_by_tag' 
#PUSH_URL = BASE_URL + '/push/'
#BATCH_PUSH_URL = BASE_URL + '/push/batch/'
BROADCAST_URL = BASE_URL + '/broadcast'
#FEEDBACK_URL = BASE_URL + '/device_tokens/feedback/'
PUSH_TO_DEVICE_URL = BASE_URL + '/push_to_device'
PUSH_TO_ALIAS_URL = BASE_URL + '/push_to_alias'

#Add/update tags
ADD_TAG_TO_ALIAS_URL = BASE_URL + '/add_tag_to_alias' 
ADD_TAG_TO_DEVICE_URL = BASE_URL + '/add_tag_to_device' 

##De-register
DEREGISTER_ALIAS_URL        = DEVICE_TOKEN_URL + '/deregister_alias'
DEREGISTER_DEVICE_URL       = DEVICE_TOKEN_URL + '/deregister_device'
