PushNotif
=========

Python Client for sending pushnotifs using PushNotif service

PushNotif provides a rich and robust, but easier to use API, to send push notifications to iPhone devices. iPhone app developers must use this service if they want to send targeted push notifications to their app users.

##Features

###Filter
* Location based: Send a push notification to all the uesrs, within a radius of R miles, from center (lat, lng)
* Tag Based filtering: Send push notification to all users where [tag1="some-value-for-tag1" [AND/OR tag2="some-value-for-tag2"]...]

###Tag
This service allows you to tag a user/device with few tags with user generated content values
e.g. tag userid="123123" with tag1="male" and tag2="gamer" .... tag5="somevaluefortag5"

This service also allows you to tag a user/device with geo tag i.e. latitude and longitude information
tag userid="123123" with geotag=(34.12,-122.24)
