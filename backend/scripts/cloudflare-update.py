import requests, os

stage = os.environ.get('STAGE', None)
if stage and stage == "PROD":
  ip = requests.get("https://checkip.amazonaws.com").text.strip()
  print(f"Updating ip to {ip}")
  zone_id = os.environ["CF_ZONE_ID"]
  record_id = os.environ["CF_RECORD_ID"]
  token = os.environ["CF_API_TOKEN"]

  url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
  headers = {
      "Authorization": f"Bearer {token}",
      "Content-Type": "application/json"
  }
  data = {
      "type": "A",
      "name": "location-locator-backend.lochlan.cc",
      "content": ip,
      "ttl": 60,
      "proxied": True
  }
  res = requests.put(url, json=data, headers=headers)
  print(res.status_code, res.text)
else: 
    print("Non-prod stage, not updating DNS")
