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


###Aliases



##How To Use

    #initialize client before making any calls
    push_notif_client = Pushnotif(YOUR_KEY_HERE, YOUR_SECRET_HERE)

    #Broadcasts to all users, registered through this app
    push_notif_client.broadcast()

    #Target send by geo tag
    push_notif_client.pushByGeo(lat=34.12,lng=-122.23,radius=10,"Hello Users")

    #Target send by custom tags
    push_notif_client.pushByTag(123, "Hello Friends", tag1="male", tag3="night")

    #Sends could be simple too!!!!!!

    #Send by device token
    push_notif_client.pushToDevice("Hey User!!", "DEVICE_TOKEN_HERE")

    #Send to alias
    #Alias, is a easily identified handle for  a device token
    #see description of alias above
    #This method takes a single or list of aliases
    #aliases could be something as simple as user ids
    push_notif_client.pushToAlias("Your awesome message here", ["userid1", "userid2"])

    #Geo tag an alias
    #Tag a user that he lives in San Francisco
    push_notif_client.addgeoTagToAlias(34.23, -123.123, "userid")

    #Add a custom tag to alias
    push_notif_client.addTagToAlias("userid", tag1="female", tag2="34")
