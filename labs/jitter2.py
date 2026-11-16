import time, os, sys, subprocess, statistics
def run(n=1500, period=0.010):
    t0=time.perf_counter(); lat=[]; nextt=t0
    for i in range(n):
        nextt += period
        d = nextt - time.perf_counter()
        if d>0: time.sleep(d)
        lat.append((time.perf_counter()-(t0+(i+1)*period))*1000)
    lat=lat[10:]; q=lambda p: sorted(lat)[int(p*len(lat))-1]
    return dict(p50=round(q(.5),3), p99=round(q(.99),3), maxi=round(max(lat),3))
print('idle      :', run())
load=[subprocess.Popen([sys.executable,'-c','while True: pass']) for _ in range(4)]
try:
    print('4 CPU hog :', run())
finally:
    [p.kill() for p in load]
