from jose import jwt
secret_key ="your-secure-secret-key-with-at-least-32-characters"
payload = {"sub": "53504c90-b259-4dea-b5f6-adab0680a650", "role": "user"}
token = jwt.encode(payload, secret_key, algorithm="HS256")
print(token)