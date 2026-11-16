import math
def size(lam, w_ms, cap_per_node=60, util=0.6, threads_per_node=64):
    nodes=math.ceil(lam/(cap_per_node*util))
    per=lam/nodes
    conc=per*(w_ms/1000)
    return nodes, round(per,1), round(conc,1), threads_per_node
print(f"{'λ (rps)':>8s} {'W p99':>7s} | {'node':>5s} {'rps/node':>9s} {'đồng thời/node':>15s} {'trần thread 64':>15s}")
for lam,w in [(50,120),(200,120),(500,120),(500,250),(1000,120),(2000,120),(2000,250)]:
    n,per,conc,th=size(lam,w)
    ok='OK' if conc<th*0.8 else 'CHẠM TRẦN → tăng node hoặc giảm W'
    print(f"{lam:8d} {w:7d} | {n:5d} {per:9.1f} {conc:15.1f} {ok:>15s}")
print()
print("Kiểm chéo bằng Little: L = λW toàn hệ =", {lam: round(lam*0.12,0) for lam in (50,200,500,1000,2000)})
