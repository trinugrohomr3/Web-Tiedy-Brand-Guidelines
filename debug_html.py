import re
with open('debug_page.html', 'r', encoding='utf-16le', errors='ignore') as f:
    content = f.read()

print(f"Content length: {len(content)}")
# Look for some common markers
print("Sample content from index 1000 to 2000:")
print(content[1000:2000])

# Try a simpler regex to see if we can find product names
names = re.findall(r'<div[^>]*class="[^"]*pro-name[^"]*"[^>]*>.*?<a[^>]*>(.*?)</a>', content, re.S | re.IGNORECASE)
print(f"Found {len(names)} names. Samples: {names[:5]}")

imgs = re.findall(r'<img[^>]*src="([^"]+)"', content, re.IGNORECASE)
print(f"Found {len(imgs)} imgs. Samples: {imgs[:5]}")
