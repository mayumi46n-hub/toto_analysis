import requests

url = "https://www.toto-dream.com/dci/I/IPB/IPB01.do?op=initLotResultLsttoto"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=20)
response.raise_for_status()

with open("data/toto_result_page.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("HTMLを保存しました")