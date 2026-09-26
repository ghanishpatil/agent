t = open("/work/bundle.js", encoding="utf-8").read()
import re

# Find the main App component region: from "Super Safe React" to "Report to admin"
start = t.find("Super Safe React")
end = t.find("Report to admin")
seg = t[start-2000:end+800]
print("=== APP COMPONENT REGION ===")
print(seg)
