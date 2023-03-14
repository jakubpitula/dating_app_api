# dating_app_api

Deployed on Deta, using JWT for Firebase authentication.

### 1. Sign-up 
#### Request type - POST
Endpoint - https://y2ylvp.deta.dev/signup  
Required request fields (order irrelevant):  
    "email"  
    "password"  
    "first_name"  
    "last_name"  
    "conf_pass"  
    "age"   
    "gender"   
    
#### Constraints:   
password - 6 characters or longer   
gender - 'm', 'f' - standing for male, female
age - integer, 18 or more

If successful, returns HTTP response 200 with  
'uid': created user id

### 2. Login
#### Request type - POST
Endpoint - https://y2ylvp.deta.dev/token  
Required form_data (!) fields:  
    "username"  
    "password"   
NB: Use the username field to input email. 

If successful, returns HTTP response 200 with  
"access_token": jwt   
"token_type": "bearer"
### 3. Currently authenticated user data 
#### Request type - GET
endpoint - https://y2ylvp.deta.dev/users/me   
Required request header:  
Key: Authentication  
Value: "Bearer {jwt}"

If successful, returns HTTP response 200 with   
'name': username   
'email': email   
'gender': gender   
'age': age   
### 4. Any user data
#### Request type - GET
endpoint - https://y2ylvp.deta.dev/users/{uid}- put the id of the user in place of {uid}, eg. https://y2ylvp.deta.dev/user/TrUilQqV21YetH16a9MX0Cy1PWJ2

If successful, returns HTTP response 200 with   
'name': username   
'gender': gender   
'age': age   
### 5. Updating (currently logged in) user data
#### Request type - PUT
endpoint - https://y2ylvp.deta.dev/users/update
Required request header:  
Key: Authentication  
Value: "Bearer {jwt}"

Optional PUT request fields (order irrelevant):  
    "email"  
    "name"  
    "age"   
    "gender"  
    "profilePicUrl"   

### 6. Setting user's preferences
#### Request type - POST
endpoint - https://y2ylvp.deta.dev/users/preferences  

Required request header:  
Key: Authentication  
Value: "Bearer {jwt}"

Required request fields (order irrelevant):  
"distance"   
"sex"   
"age_min"   
"age_max"   

### 7. Setting user's interests
#### Request type - POST
endpoint - https://y2ylvp.deta.dev/users/interests  

Required request header:  
Key: Authentication  
Value: "Bearer {jwt}"

Required request fields (order irrelevant):  
"hobbies"   
"about"   
"zodiac"   
"communication"   
"workout"   
"drinking"   
"smoking"   


### 8. Adding friends
#### Request type - POST
endpoint - https://y2ylvp.deta.dev/users/friends  

Required request header:  
Key: Authentication  
Value: "Bearer {jwt}"

Required request fields (order irrelevant):  
"uid" - of the new friend   

### 9. Reading friends
#### Request type - GET
endpoint - https://y2ylvp.deta.dev/users/friends  

Required request header:  
Key: Authentication  
Value: "Bearer {jwt}"