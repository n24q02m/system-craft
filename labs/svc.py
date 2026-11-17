import json, datetime, subprocess, decimal, os, sys, tempfile
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
payload = {
  "tien": decimal.Decimal("1234567.89"),
  "emoji": "Ổn định 🚀 — tiếng Việt có dấu",
  "ngay_dst": "2026-03-08T02:30:00-05:00",
  "rong": ""
}
def py_roundtrip(p):
    s = json.dumps({k: (str(v) if isinstance(v, decimal.Decimal) else v) for k, v in p.items()}, ensure_ascii=False)
    return s
print("PY  →", py_roundtrip(payload)[:120])
js = '''
let buf="";process.stdin.on("data",d=>buf+=d).on("end",()=>{
  const o=JSON.parse(buf);
  const out={ tien:Number(o.tien), emoji:o.emoji, ngay_dst:new Date(o.ngay_dst).toISOString(), rong:o.rong };
  console.log(JSON.stringify(out));
});'''
s = py_roundtrip(payload)
with tempfile.TemporaryDirectory() as td:
    js_path = os.path.join(td, "svc.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js)
    r = subprocess.run(
        ["node", js_path],
        input=s,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
print("JS  ←", r.stdout.strip())
back = json.loads(r.stdout)
fails=[]
if str(back['tien']) != "1234567.89": fails.append('tien')
if back['emoji'] != payload['emoji']: fails.append('emoji')
if back['ngay_dst'] != "2026-03-08T07:30:00.000Z": fails.append('ngay_dst')
if back['rong'] != "" and back['rong'] is not None: fails.append('rong')
print("FAIL:", fails or "khong co")
