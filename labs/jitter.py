import time, statistics, sys, os, subprocess
def run(n=3000, period=0.010, mode='deadline'):
    t0=time.perf_counter(); lat=[]; nextt=t0
    for i in range(n):
        if mode=='sleep':
            time.sleep(period)
        else:
            nextt += period
            d = nextt - time.perf_counter()
            if d>0: time.sleep(d)
        lat.append((time.perf_counter()-(t0+(i+1)*period))*1000)  # trễ so với lịch lý tưởng, ms
    lat=[x for x in lat[10:]]
    q=lambda p: sorted(lat)[int(p*len(lat))-1]
    return dict(n=len(lat), p50=round(q(.5),3), p90=round(q(.9),3), p99=round(q(.99),3),
                maxi=round(max(lat),3), mean=round(statistics.mean(lat),3))
print('CPU:', os.cpu_count())
print('naive sleep  :', run(mode='sleep'))
print('deadline sched:', run(mode='deadline'))
