# L12 — mô hình chi phí 2 mức quant (roofline, KHÔNG phải benchmark)
P=8e9            # tham số (Llama-3.1-8B)
L,H_kv,D=32,8,128
HBM={'H100-SXM':3.35e12,'L40S':8.64e11,'A10G':6e11,'RTX4090':1.008e12}
GPU_HR={'H100-SXM':2.50,'L40S':1.20,'A10G':0.75,'RTX4090':0.45}   # USD/giờ, giả định — bạn thay giá thật
def kv_bytes(seq, bytes_per=2):
    return 2*L*H_kv*D*seq*bytes_per
print("KV cache / token (fp16): %.0f KiB" % (kv_bytes(1)/1024))
for seq in (4096, 32768, 131072):
    print("  seq=%-7d → %.2f GiB/sequence" % (seq, kv_bytes(seq)/2**30))
print()
print(f"{'GPU':10s} {'Băng thông':>11s} | {'fp16':>6s} {'int8':>6s} {'int4':>6s}  (tok/s trần batch=1)")
rows=[]
for g,bw in HBM.items():
    vals=[]
    for bpw,label in ((2,'fp16'),(1,'int8'),(0.5,'int4')):
        w=P*bpw                       # byte phải đọc mỗi bước decode
        tps=bw/w
        vals.append(tps)
    print(f"{g:10s} {bw/1e12:8.2f} TB/s | {vals[0]:6.0f} {vals[1]:6.0f} {vals[2]:6.0f}")
    rows.append((g,vals))
print()
print("Chi phí / 1 triệu token sinh ra (batch=1, hiệu dụng 70% trần, giá thuê giả định):")
for g,vals in rows:
    line=f"  {g:10s}"
    for (bpw,label),tps in zip(((2,'fp16'),(1,'int8'),(0.5,'int4')),vals):
        eff=tps*0.7
        cost=GPU_HR[g]/ (eff*3600) *1e6
        line+=f"  {label}={cost:8.2f}$"
    print(line)
print()
print("Nghịch lý cần nhớ: int4 KHÔNG làm GPU rẻ hơn — nó làm CÙNG một GPU phục vụ nhiều token hơn.")
print("Nếu SLA là latency (TTFT/tok/s của MỘT người dùng) thì int4 giúp; nếu SLA là throughput thì")
print("nút cổ chai chuyển sang compute (FLOPs) và sang KV cache — đo lại, đừng suy từ bảng này.")
