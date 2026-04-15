import subprocess, re
url = 'https://www.nb-liao.com/products/17.html'
cmd = ['curl.exe', '-A', 'Mozilla/5.0', '-s', url]
res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')

# The website might embed images in a JS variable. Let's find all absolute URLs.
print(re.findall(r'https://omo-oss-image.thefastimg.com[^\"]+\.(?:png|jpg)', res.stdout)[:10])

# Are there names close to it? Let's check the area.
