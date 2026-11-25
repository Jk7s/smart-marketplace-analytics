import hashlib, math, re, time
from collections import Counter
import numpy as np

def tokenize(text):
    return re.findall(r"[a-z0-9]+", (text or "").lower())

def keyword_score(query, product):
    q=set(tokenize(query))
    if not q: return 0.0
    words=tokenize(product["title"]+" "+product["description"]+" "+product["category"])
    counts=Counter(words)
    return sum(1 + math.log1p(counts[t]) for t in q if t in counts) / len(q)

def fixed_vector(text, dimensions=64):
    """Deterministic feature-hash vector; no paid model/API required."""
    vec=np.zeros(dimensions, dtype=float)
    tokens=tokenize(text)
    for token in tokens:
        h=int(hashlib.md5(token.encode()).hexdigest(),16)
        vec[h % dimensions] += 1 if (h >> 8) % 2 else -1
    norm=np.linalg.norm(vec)
    return vec/norm if norm else vec

def cosine_similarity(a,b):
    na=np.linalg.norm(a); nb=np.linalg.norm(b)
    return float(np.dot(a,b)/(na*nb)) if na and nb else 0.0

def search_products(products, query, max_price=60000, category="All",
                    in_stock=True, mode="Hybrid", limit=30):
    candidates=[]
    qvec=fixed_vector(query)
    for p in products:
        if p["price"] > float(max_price): continue
        if category != "All" and not p["category"].startswith(category): continue
        if in_stock and p["stock"] <= 0: continue
        kw=keyword_score(query,p)
        semantic=cosine_similarity(qvec, fixed_vector(p["title"]+" "+p["description"]+" "+p["category"]))
        if mode=="Keyword": score=kw
        elif mode=="Vector": score=semantic
        else: score=0.55*kw+0.45*semantic
        # Lightweight reranking: modest preference for available items and exact title phrase.
        phrase=1.0 if query.lower().strip() and query.lower().strip() in p["title"].lower() else 0.0
        score=score + 0.08*phrase + (0.02 if p["stock"]>0 else 0)
        candidates.append({**p,"keyword_score":round(kw,4),
                           "vector_score":round(semantic,4),"rank_score":round(score,4)})
    return sorted(candidates,key=lambda x:x["rank_score"],reverse=True)[:int(limit)]

def near_duplicate_candidates(products, threshold=0.82):
    """Candidate generation by token-set Jaccard similarity; exact equality is separately checked."""
    result=[]
    sample=products[:300]
    for i,a in enumerate(sample):
        ta=set(tokenize(a["title"]+" "+a["description"]))
        for b in sample[i+1:]:
            tb=set(tokenize(b["title"]+" "+b["description"]))
            union=ta|tb
            score=len(ta&tb)/len(union) if union else 0
            if score>=threshold:
                result.append({"product_a":a["id"],"product_b":b["id"],
                               "similarity":round(score,3),
                               "exact_match":(a["title"],a["description"])==(b["title"],b["description"])})
                if len(result)>=100: return result
    return result

def percentile(values, p):
    if not values: return 0.0
    return float(np.percentile(np.asarray(values,dtype=float),p))

def approximate_unique_count(values, precision=10):
    """Small HyperLogLog-style estimate using hashed leading-zero buckets."""
    m=2**precision
    registers=[0]*m
    for value in values:
        h=int(hashlib.sha1(str(value).encode()).hexdigest()[:16],16)
        idx=h & (m-1)
        w=h >> precision
        rank=(64-precision+1) if w==0 else (64-precision+1-w.bit_length()+1)
        registers[idx]=max(registers[idx],rank)
    alpha=0.7213/(1+1.079/m)
    estimate=alpha*m*m/sum(2.0**(-r) for r in registers)
    zeros=registers.count(0)
    if estimate <= 2.5*m and zeros: estimate=m*math.log(m/zeros)
    return max(0,int(round(estimate)))

def benchmark_scan(products, price_limit=60000):
    start=time.perf_counter()
    result=[p for p in products if p["price"]<=price_limit and p["stock"]>0]
    elapsed=(time.perf_counter()-start)*1000
    return len(result), elapsed, len(products)

def shard_replica_experiment(products, shards=4):
    buckets=[[] for _ in range(shards)]
    for p in products: buckets[p["id"]%shards].append(p)
    replicas=[list(buckets[i]) for i in range(shards)]
    return [{"shard":i,"primary_records":len(buckets[i]),
             "replica_records":len(replicas[i]),
             "sample_ids":[p["id"] for p in buckets[i][:5]]} for i in range(shards)]
