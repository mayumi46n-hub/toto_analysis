import sys
import requests

if len(sys.argv) >= 2:
    round_no = int(sys.argv[1])
else:
    round_no = 1636

hold_cnt_id = f"{round_no:04d}"

url = (
    "https://store.toto-dream.com/dcs/subos/screen/pi04/spin011/"
    f"PGSPIN01101LnkHoldCntLotResultLsttoto.form?popupDispDiv=disp&holdCntId={hold_cnt_id}"
)
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=20)
response.raise_for_status()

with open(f"data/toto_round_{round_no}.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"第{round_no}回のHTMLを保存しました")