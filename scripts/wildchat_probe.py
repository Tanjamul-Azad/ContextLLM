import json, random, re, sys, time, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
BASE="https://datasets-server.huggingface.co"; DS="allenai/WildChat-1M"
def get(u):
    for _ in range(4):
        try:
            with urllib.request.urlopen(u, timeout=60) as r: return json.load(r)
        except Exception as e: err=e; time.sleep(15)
    return None
random.seed(11)
offs=sorted(random.sample(range(0,837989-100),40))
PAT={
 "requirement":[r"\bfollow (this|the following|that) (format|template|structure|style|example)",r"\b(in|use) (this|the same|the following) (format|template|structure)",r"\bexactly like (this|that|the)",r"\bsame (format|structure|style) as\b",r"\bhere is an example\b",r"\blike this example\b"],
 "analogy":[r"\bsimilar to\b",r"\bin the same way (as|that)\b",r"\binspired by\b",r"\banalog(y|ous)\b",r"\bjust like\b",r"\bthe way (that )?\w+ (does|did|works|handles)"],
 "counter":[r"\b(don'?t|do not) (do it|write it|make it) like\b",r"\bnot like (this|that|the previous|the last|before)",r"\bunlike (this|that|the)\b",r"\b(avoid|don'?t use) (something like|phrases like|words like)\b",r"\b(don'?t|do not) (copy|repeat) (the|this|that)\b"],
 "generic":[r"\bfor example\b",r"\bfor instance\b",r"\be\.g\.",r"\blike this:"],
}
C={k:[re.compile(p,re.I) for p in v] for k,v in PAT.items()}
seen=set(); uniq_turns=0; eng=0; conv=0
hits={k:0 for k in PAT}; short={k:0 for k in PAT}; ex={k:[] for k in PAT}
for o in offs:
    d=get(f"{BASE}/rows?dataset={DS}&config=default&split=train&offset={o}&length=100")
    if d is None: continue
    for row in d["rows"]:
        r=row["row"]; conv+=1
        if r.get("language")!="English": continue
        eng+=1
        for t in r["conversation"]:
            if t.get("role")!="user": continue
            x=(t.get("content") or "").strip()
            key=x[:200]
            if key in seen: continue
            seen.add(key); uniq_turns+=1
            for k,ps in C.items():
                if any(p.search(x) for p in ps):
                    hits[k]+=1
                    if len(x)<1200:
                        short[k]+=1
                        if len(ex[k])<25: ex[k].append(x[:300].replace("\n"," "))
    time.sleep(2.5)
print(json.dumps({"conversations":conv,"english":eng,"unique_english_user_turns":uniq_turns,"hits_unique":hits,"hits_unique_under_1200_chars":short},indent=1))
json.dump(ex,open(sys.argv[1],"w",encoding="utf-8"),ensure_ascii=False,indent=1)
