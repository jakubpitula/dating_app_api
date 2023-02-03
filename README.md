# dating_app_api

Deployed on Deta, using JWT for Firebase authentication.

### 1. Sign-up 
#### Request type - POST
Endpoint - https://y2ylvp.deta.dev/signup  
Required POST request fields (order irrelevant):  
    "email"  
    "password"  
    "first_name"  
    "last_name"  
    "conf_pass"  
    "age"   
    "gender"   
    
#### Constraints:   
password - 6 characters or longer   
gender - 'm', 'f', 'nb' or 'pns' - standing for male, female, non-binary, prefer not to say   

If successful, returns HTTP response 200 with  
'uid': created user id

### 2. Login
#### Request type - POST
Endpoint - https://y2ylvp.deta.dev/login  
Required POST request fields:  
    "email"  
    "password"

If successful, returns HTTP response 200 with  
"token": jwt
### 3. Currently authenticated user data 
#### Request type - GET
endpoint - https://y2ylvp.deta.dev/get_current_user  
Required GET request header:  
Key: Authentication  
Value: jwt

If successful, returns HTTP response 200 with   
'name': username   
'email': email   
'gender': gender   
'age': age   
### 4. Arbitrary user data
#### Request type - POST
endpoint - https://y2ylvp.deta.dev/get_user_data
Required POST request header:  
Key: Authentication  
Value: jwt

Required Get request fields:  
    "uid"

If successful, returns HTTP response 200 with   
'name': username   
'email': email   
'gender': gender   
'age': age   
### 5. Updating (currently logged in) user data
#### Request type - PUT
endpoint - https://y2ylvp.deta.dev/user/{uid}  -  put the id of the user whose data is to be changed in place of {uid}, eg. https://y2ylvp.deta.dev/user/TrUilQqV21YetH16a9MX0Cy1PWJ2   
Required PUT request header:  
Key: Authentication  
Value: jwt

Optional PUT request fields (order irrelevant):  
    "email"  
    "name"  
    "age"   
    "gender" 
