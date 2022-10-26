import requests
import json
url = 'URL/webservice/rest/server.php'
users = {
         "wstoken": "YOUR TOKEN",
         "wsfunction": "core_user_create_users",
         "moodlewsrestformat": "json",
         "users[0][username]": "USERNAME",
         "users[0][email]": "EMAIL",
         "users[0][lastname]": "LASTNAME",
         "users[0][firstname]": "FIRSTNAME",
         "users[0][password]": "PASSWORD", # OR "users[0][createpassword]": 1
         "users[0][auth]": "manual",
         "users[0][timezone]": "TIMEZONE"
}
response = requests.request("POST", url=url, params=users)
print(json.dumps(response.json(), indent=4))
