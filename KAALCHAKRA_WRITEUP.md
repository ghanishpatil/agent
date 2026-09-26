When I opened the challenge at http://138.199.163.92:10675/docs, I saw a FastAPI Swagger documentation page with the title "Tick tick tick ...." The description said "Interact with the mysterious AI oracle. Some inputs resonate more than others." The challenge was about an ML model trained to study the "cyclic nature of time" and I needed to find the trigger to reveal the flag.

I checked the OpenAPI spec at /openapi.json to understand the API structure. There was a single endpoint POST /predict that accepts two parameters: "text" (string) and "timestamp" (string). The response returns a score, progress percentage, and a tone message. This looked straightforward - I needed to find the right combination of text and timestamp.

I started testing different text inputs related to time and cycles. The challenge name "Kaalchakra" is Sanskrit for "wheel of time", so I tried variations of these words. I wrote a script to test keywords systematically:

```python
import requests

base_url = "http://138.199.163.92:10675"
timestamp = "2024-01-01T00:00:00"

keywords = ["time", "cycle", "kaal", "chakra", "wheel", "kaalchakra", 
            "time cycle", "wheel of time", "time wheel"]

for text in keywords:
    response = requests.post(f"{base_url}/predict", 
                           json={"text": text, "timestamp": timestamp})
    data = response.json()
    print(f"{text}: Progress {data['progress']}%")
```

The results were interesting:
- "time" gave 56% progress
- "wheel" gave 72% progress
- "wheel of time" gave 91% progress
- "time wheel" gave 100% progress!

Perfect! But when I looked at the full response for "time wheel", it still said `"tone": "Bravo ! Almost there."` even though progress was 100%. Something was still missing.

I tried everything I could think of. I tested different timestamp formats, cyclic patterns like "2024-12-12T12:12:12", special dates like Unix epoch, leap years, solstices. I tried sending multiple requests in sequence thinking maybe it needed a "cycle" of requests. I even tried parameter pollution, injection attacks, and checking for hidden endpoints. Nothing worked - every response was the same "Almost there" message.

Then I stepped back and thought about the challenge title again: "cyclic nature of time." What if this wasn't about finding a special timestamp in the past, but about the actual current time? Time is cyclic - it keeps moving forward. Maybe the timestamp needed to be synchronized with the server's current time, not some static historical value.

I checked the HTTP response headers and noticed the server was sending a Date header with its current time. I had a hunch - what if I needed to use the server's actual current time as the timestamp?

I modified my script to grab the server time and use it:

```python
import requests
from email.utils import parsedate_to_datetime

base_url = "http://138.199.163.92:10675"

# Get current server time from response headers
r = requests.get(f"{base_url}/")
server_date = r.headers.get("date")
print(f"Server time: {server_date}")

# Parse it to ISO format
server_dt = parsedate_to_datetime(server_date)
timestamp = server_dt.isoformat()

# Send the request with current server time
response = requests.post(
    f"{base_url}/predict",
    json={"text": "time wheel", "timestamp": timestamp}
)

print(response.json())
```

When I ran this, the response completely changed:

```json
{
  "label": "Kaal{Tareekh_pe_tareekh}",
  "score": 1.0000001192092896,
  "message": "You got me :) "
}
```

There it was! The flag appeared when I used the current server time instead of a static timestamp. The "cyclic nature of time" literally meant that time keeps cycling - you need to sync with the present moment, not use historical timestamps. It was a clever misdirection making it look like an ML challenge when it was really about time synchronization.

The flag "Tareekh pe tareekh" is a famous Bollywood dialogue meaning "date after date" - a perfect reference for this time-based challenge!

Flag: Kaal{Tareekh_pe_tareekh}

Team Exploit4
