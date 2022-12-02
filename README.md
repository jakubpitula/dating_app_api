# dating_app_api

Deployed on Deta, using JWT for Firebase authentication.

### 1. Sign-up 
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
Endpoint - https://y2ylvp.deta.dev/login  
Required POST request fields:  
    "email"  
    "password"

If successful, returns HTTP response 200 with  
"token": jwt
### 3. Currently authenticated user data 
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
