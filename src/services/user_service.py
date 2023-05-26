import requests
from fastapi import HTTPException

def check_if_user_exists_by_id(user_id):
  user_service_url = f"http://user-service:80/api/users/{user_id}"
  response = requests.get(user_service_url)

  if response.status_code != 200:
    raise HTTPException(
            status_code=404, detail="User not found")
  
  return response.json()