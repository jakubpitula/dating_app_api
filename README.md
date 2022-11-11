# dating_app_api

Deployed on Deta, using JWT for Firebase authentication.

### 1. Sign-up 
Endpoint - https://y2ylvp.deta.dev/signup  
Required request fields (order irrelevant):  
    "email"  
    "password"  
    "first_name"  
    "last_name"  
    "conf_pass"  

If successful, returns HTTP response 200 with  
'uid': created user id

### 2. Login
Endpoint - https://y2ylvp.deta.dev/login  
Required request fields:  
    "email"  
    "password"

If successful, returns HTTP response 200 with  
"token": jwt
### 3. Validation 
endpoint - https://y2ylvp.deta.dev/validate  
Required header:  
Key: Authentication  
Value: jwt

If successful, returns HTTP response 200 with
'uid': user id
