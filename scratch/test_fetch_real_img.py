import urllib.request
import re

urls = [
    'https://www.archanaskitchen.com/recipe/masala-karela-recipe',
    'https://www.archanaskitchen.com/recipe/spicy-schezuan-vegetarian-noodles-recipe',
    'https://www.archanaskitchen.com/recipe/spicy-thakkali-rice-tomato-pulihora'
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for u in urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            m = re.search(r'https://images\.archanaskitchen\.com/images/recipes/[^"]+\.jpg', html)
            if not m:
                m = re.search(r'https://storage\.googleapis\.com/ak_strapi_cms_gcp/images/recipes/[^"]+\.jpg', html)
            print(u, '-->', m.group(0) if m else 'No match')
    except Exception as e:
        print(u, '--> Error:', e)
