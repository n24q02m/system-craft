# L13 — sizing bằng định luật Little + ngân sách lỗi (ví dụ: lớp tải OLTP sổ cái)
def little(lam, w_ms, headroom=0.6, per_node_rps=180):
    L = lam * (w_ms/1000)                 # số request đồng thời (in-flight) theo Little
    L_design = L / headroom               # giữ CPU ≤60% để còn chỗ cho đỉnh
    nodes = -(-int(L_design*3)//int(per_node_rps))  # ceil(L_design / per_node_rps)  (xấp xỉ 3 luồng/node)
    return L, L_design, max(nodes,1)
print(f"{'λ (rps)':>8s} {'W p99 (ms)':>11s} {'L = λW':>8s} {'L thiết kế (60%)':>17s} {'node ≈':>7s} {'$ /tháng @0.045/h':>18s}")
for lam,w in [(50,120),(500,120),(500,250),(2000,120),(2000,250),(20000,80)]:
    L,Ld,n = little(lam,w)
    print(f"{lam:8d} {w:11d} {L:8.0f} {Ld:17.0f} {n:7d} {n*0.045*730:18.0f}")
print()
print("Kết nối DB cần: L_design × (1 + hệ số pool dư) — nếu mỗi request giữ 1 kết nối trong 8 ms,")
print("số kết nối đồng thời = λ × 0,008; phần còn lại của W là CPU/GC/mạng, KHÔNG cần kết nối.")
for lam in (500,2000,20000):
    print(f"  λ={lam:6d} rps · giữ kết nối 8 ms → {lam*0.008:6.0f} kết nối đồng thời (làm tròn pool = ×1,5 = {lam*0.008*1.5:6.0f})")
print()
print("Ngân sách lỗi (SLO 99,9% tháng 30 ngày = 43,2 phút):")
budget=43.2
for name,outage in [("1 sự cố 10 phút",10),("1 sự cố 25 phút",25),("3 sự cố 10 phút",30),("deploy hỏng 1 lần 45 phút",45)]:
    print(f"  {name:26s} tiêu {outage/budget*100:6.1f}% ngân sách")
