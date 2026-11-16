import json, subprocess
payload = {"id_don": 9007199254740993, "tien": 1234567.89, "tien2": 0.1+0.2,
           "emoji":"Ổn định 🚀", "ngay_dst":"2026-03-08T02:30:00-05:00", "rong":""}
s = json.dumps(payload, ensure_ascii=False)
print("PY gửi :", s)
r = subprocess.run(['node','-e','''
let b="";process.stdin.on("data",d=>b+=d).on("end",()=>{const o=JSON.parse(b);
console.log(JSON.stringify({id_don:o.id_don,tien:o.tien,tien2:o.tien2,emoji:o.emoji,
 ngay:new Date(o.ngay_dst).toISOString(),rong:o.rong,rong_type:typeof o.rong}));});'''],
 input=s, capture_output=True, text=True)
print("JS trả :", r.stdout.strip(), r.stderr.strip()[:100])
b=json.loads(r.stdout)
fails=[]
if b["id_don"]!=payload["id_don"]: fails.append("id_don (int64 > 2^53)")
if abs(b["tien"]-payload["tien"])>1e-9: fails.append("tien")
if b["tien2"]!=payload["tien2"]: fails.append("tien2 (0.1+0.2)")
if b["emoji"]!=payload["emoji"]: fails.append("emoji")
if b["ngay"]!="2026-03-08T07:30:00.000Z": fails.append("ngay_dst")
print("FAIL:", fails)
