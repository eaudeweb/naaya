import json
json_data = {}
for (uid, user) in app.pite.acl_users.data.items():
    json_data[user.email] = {'%uid%': uid,
                             '%pass%': user.__,
                             '%firstname%': user.firstname,
                             '%lastname%': user.lastname}

output = json.loads(json_data)