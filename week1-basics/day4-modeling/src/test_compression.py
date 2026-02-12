import numpy as np
import joblib
import time
import os

X = np.random.rand(20_000_000).astype(np.float32) 

def test_compression(level):
    filename = f"X_c{level}.joblib"
    
    t0 = time.time()
    joblib.dump(X, filename, compress=level)
    save_time = time.time() - t0
    
    t0 = time.time()
    _ = joblib.load(filename)
    load_time = time.time() - t0
    
    size_mb = os.path.getsize(filename) / (1024**2)
    
    return save_time, load_time, size_mb

levels = [0, 3, 9]

for lvl in levels:
    save_t, load_t, size = test_compression(lvl)
    print(f"[compress={lvl}] save: {save_t:.3f}s | load: {load_t:.3f}s | size: {size:.1f}MB")


##
# 너무 압축을 해버리니까 저장 시간만 보자면 0,3 은 100배차이
# load 도 20배 이상?? 정도 차이나는데 속도랑 용량은 결국 하나는 포기해야하는구나  
# 그렇다면 0 과 3 과 9 어떤 경우에서 사용해야할까 ??? 
##