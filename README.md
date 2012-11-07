PushNotif
=========

Python Client for sending pushnotifs using PushNotif service

PushNotif provides a rich and robust, but easier to use API, to send push notifications to iPhone devices. iPhone app developers must use this service if they want to send targeted push notifications to their app users.

##Features

###Filter
* Location based: Send a push notification to all the uesrs, within a radius of R miles, from center (lat, lng)
e.g. send push notification to all users within a radius of 10 miles around (34.23, -122.45) `(lat,lng) = (34.23, -122.45) and radius=10)`

* Tag Based filtering: Send push notification to all users where [tag1="some-value-for-tag1" [AND tag2="some-value-for-tag2"]...] 
e.g. send push notification to all users with `tag1="male" and tag3="42"`


###Tag
* Custom Content Tags: This service allows you to tag a user/device with few tags with custom values 
e.g. `tag userid="123123" tag1="male" and tag2="gamer" and tag5="somevaluefortag5"`

* Geo Tag: This service also allows you to tag a user/device with geo tag i.e. latitude and longitude 
e.g. `tag userid="123123" with geotag=(34.12,-122.24)`
