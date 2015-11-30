# API v1

You need to send following headers with every request:

    X-Sensor-Version: 1

## Create an user

To create a new user you can send following POST request.

    POST http://data.example.org/users

    HTTP/1.1
    Host: data.example.org
    X-Sensor-Version: 1
    Content-Type: application/json

    {
        "email":"test@example.org",
        "password":"supersecretpassword"
    }

The response will be in case of success following:

    HTTP/1.1 200 Success

    Content-Type: application/json

    {
        "id": 1,
        "email": "test@example.org",
        "created_at": "2015-02-07 12:34:56"
    }

In case the request fails because the email address is already used by another
user it will answer with a `409 Conflict`:

    HTTP/1.1 409 Conflict

    Content-Type: application/json

    {
        "message": "Email address already in use."
    }

## Confirm user email address

After adding a new user you will get send an email with a link to open. This
is the only resource that doesn't need the `X-Sensor-Version` header.

    GET http://data.example.org/users/1/{randomToken}

## Create a sensor

To create a new sensor you need to send following POST request. The given email
address needs to be an already registered one. The parameter `name` is optional.

    POST http://data.example.org/sensors

    HTTP/1.1
    Host: data.example.org
    X-Sensor-Version: 1
    Content-Type: application/json

    {
        "email":"test@example.org",
        "name":"My new sensor"
    }

You then get following response on success:

    HTTP/1.1 200 Success

    Content-Type: text/plain

    id:1
    apikey:e8d1420b4ff41c3f12186d894a99e1c4aa681da79c47007e9dadecd9ecb0482ee1e224510e7484078c0289f34396


If the user doesn't exists you get following:

    HTTP/1.1 412 Precondition Failed

    Content-Type: application/json

    {
        "message": "User not found or not approved"
    }

If the name is not valid (more than 255 charaters) then you get following response:

    HTTP/1.1 400 Bad Request

    Content-Type: application/json

    {
        "message": "Sensor name is invalid"
    }

## Add sensor values

To add new values to the sensor you need to send following GET. The HTTP headers X-Sensor-Api-Key 
and X-Sensor-Version are mandatory. The payload is CSV containing the sensor ID as first 
column, the sensor type ID as second column, and the value of the sensor as third column.

    POST http://data.example.org/sensors/20b79b2689f8b9716
    
    HTTP/1.1
    Host: data.example.org
    X-Sensor-Api-Key: abcdef0123456789
    X-Sensor-Version: 1
    Content-Type: text/csv
    
    1,3,12.5
    2,5,123

You then get following response on success:

    HTTP/1.1 200 Success

    
If you don't send the header X-Sensor-Api-Key at all you get the following response:


    HTTP/1.1 401 Unauthorized
    
    Content-Type: application/json
    
    {
        "message": "No API key in header found"
    }


If the key is invalid you get following response:

    HTTP/1.1 401 Unauthorized
    
    Content-Type: application/json
    
    {
        "message": "Invalid API key"
    }

If some lines or values (types) are invalid, then you'll get:

    HTTP/1.1 400 Bad Request
    
    Content-Type: application/json
    
    {
        "message": "Bad CSV lines"
        "lines": [ ... ]
    }
