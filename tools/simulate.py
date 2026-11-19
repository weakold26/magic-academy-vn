#!/usr/bin/env python3
"""시나리오 전수 시뮬레이션.

- 모든 도달 가능 상태를 BFS로 탐색 (호감도·플래그 포함)
- 끊긴 링크, 도달 불가 노드, 막다른 길, 무한 루프, 엔딩 도달 여부 검사
- 대사 번역체·맞춤법·부호 패턴 점검
"""
import json
import os
import re
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "src", "data", "scenario.json")

with open(PATH, encoding="utf-8") as f:
    data = json.load(f)
nodes = data["nodes"]
meta = data["meta"]

BG_KEYS = ("hall", "greenhouse", "observatory", "lake")
WHO_KEYS = ("elize", "seia")

errors, warnings = [], []

# ---------- 1. 구조 ----------
for nid, n in nodes.items():
    targets = []
    if n.get("next"):
        targets.append(n["next"])
    for c in n.get("choices", []):
        if c.get("next"):
            targets.append(c["next"])
    for b in n.get("branch", []):
        targets.append(b["next"])
    for t in targets:
        if t not in nodes:
            errors.append("broken link %s -> %s" % (nid, t))
    if (not n.get("text") and not n.get("choices") and not n.get("branch")
            and not n.get("ending") and not n.get("next")):
        errors.append("node %s has no text/choices/ending" % nid)
    if not n.get("ending") and not n.get("next") and not n.get("choices") and not n.get("branch"):
        errors.append("dead end at %s" % nid)
    if n.get("ending") and n["ending"] not in meta["endings"]:
        errors.append("unknown ending %s at %s" % (n["ending"], nid))
    if n.get("choices") and len(n["choices"]) < 2:
        errors.append("choice with <2 options at %s" % nid)
    for slot in ("show", "show2"):
        if n.get(slot) and n[slot]["id"] not in meta["heroines"]:
            errors.append("unknown character %s at %s" % (n[slot]["id"], nid))
    if n.get("bg") and n["bg"] not in BG_KEYS:
        errors.append("unknown bg %s at %s" % (n["bg"], nid))
    for c in n.get("choices", []):
        if not c.get("next"):
            errors.append("choice without next at %s" % nid)

# ---------- 2. 도달성 ----------


def test_cond(c, aff, flags):
    if not c:
        return True
    if c.get("flag") and c["flag"] not in flags:
        return False
    if c.get("noflag") and c["noflag"] in flags:
        return False
    for k, v in (c.get("affMin") or {}).items():
        if aff.get(k, 0) < v:
            return False
    for k, v in (c.get("affMax") or {}).items():
        if aff.get(k, 0) > v:
            return False
    return True


def apply_eff(eff, aff, flags):
    a = dict(aff)
    f = set(flags)
    if eff:
        if eff.get("elize"):
            a["elize"] = a.get("elize", 0) + eff["elize"]
        if eff.get("seia"):
            a["seia"] = a.get("seia", 0) + eff["seia"]
        if eff.get("flag"):
            f.add(eff["flag"])
    return a, frozenset(f)


# 상태 공간 축소: 조건에 등장하는 플래그와 호감도 임계값만 상태에 남긴다.
USED_FLAGS = set()
THRESHOLDS = [0]
for n in nodes.values():
    conds = [c.get("when") for c in n.get("choices", [])]
    conds += [b.get("if") for b in n.get("branch", [])]
    for c in conds:
        if not c:
            continue
        if c.get("flag"):
            USED_FLAGS.add(c["flag"])
        if c.get("noflag"):
            USED_FLAGS.add(c["noflag"])
        for v in (c.get("affMin") or {}).values():
            THRESHOLDS.append(v)
        for v in (c.get("affMax") or {}).values():
            THRESHOLDS.append(v + 1)
CAP = max(THRESHOLDS) + 1


def norm_aff(aff):
    return {k: min(v, CAP) for k, v in aff.items() if v}


def key(node_id, aff, flags):
    return (node_id, aff.get("elize", 0), aff.get("seia", 0),
            frozenset(f for f in flags if f in USED_FLAGS))


start = meta["start"]
seen = {key(start, {}, frozenset())}
visited = set()
endings_hit = {}
max_aff = {"elize": 0, "seia": 0}
choice_nodes = 0
option_count = 0
queue = deque([(start, {}, frozenset())])
states = steps = 0

while queue:
    node_id, aff, flags = queue.popleft()
    states += 1
    guard = 0
    cur, cur_aff, cur_flags = node_id, aff, flags
    while True:
        guard += 1
        steps += 1
        if guard > 4000:
            errors.append("possible infinite loop near %s" % cur)
            break
        n = nodes.get(cur)
        if not n:
            errors.append("missing node %s" % cur)
            break
        visited.add(cur)
        max_aff["elize"] = max(max_aff["elize"], cur_aff.get("elize", 0))
        max_aff["seia"] = max(max_aff["seia"], cur_aff.get("seia", 0))

        if n.get("branch"):
            nxt = None
            for b in n["branch"]:
                if test_cond(b.get("if"), cur_aff, cur_flags):
                    nxt = b["next"]
                    break
            if nxt is None:
                nxt = n["branch"][-1]["next"]
            cur = nxt
            continue

        if n.get("ending"):
            endings_hit[n["ending"]] = endings_hit.get(n["ending"], 0) + 1
            break

        if n.get("choices"):
            choice_nodes += 1
            usable = [c for c in n["choices"] if test_cond(c.get("when"), cur_aff, cur_flags)]
            if not usable:
                errors.append("no available choice at %s" % cur)
            option_count += len(usable)
            for c in n["choices"]:
                if not test_cond(c.get("when"), cur_aff, cur_flags):
                    continue
                na, nf = apply_eff(c.get("eff"), cur_aff, cur_flags)
                if c.get("flag"):
                    nf = frozenset(set(nf) | {c["flag"]})
                na = norm_aff(na)
                nf = frozenset(f for f in nf if f in USED_FLAGS)
                k = key(c["next"], na, nf)
                if k not in seen:
                    seen.add(k)
                    queue.append((c["next"], na, nf))
            break

        na, nf = apply_eff(n.get("eff"), cur_aff, cur_flags)
        na = norm_aff(na)
        nf = frozenset(f for f in nf if f in USED_FLAGS)
        k = key(n["next"], na, nf)
        if k not in seen:
            seen.add(k)
            queue.append((n["next"], na, nf))
        break

unreachable = [i for i in nodes if i not in visited]
if unreachable:
    errors.append("unreachable nodes: %s" % ", ".join(unreachable[:12]))
for e in meta["endings"]:
    if e not in endings_hit:
        errors.append("ending never reached: %s" % e)

# ---------- 3. 문장 점검 ----------
BAD = [
    (r"당신", '번역체 "당신"'),
    (r"그것은|그것을|그것이 ", "지시대명사 번역체"),
    (r"할 수 있을 것이다", "번역체"),
    (r"되어진|되어지는", "이중 피동"),
    (r"  +", "연속 공백"),
    (r"되요|안되요|됬", "맞춤법(되/돼)"),
    (r"[!?]{2,}", "중복 문장부호"),
    (r"[a-zA-Z]{3,}", "영문 혼입"),
    (r"\.\.\.", "... 사용(… 권장)"),
    (r"ㅋ", "ㅋㅋ체"),
    (r"[\u30a0-\u30ff\u4e00-\u9fff]", "한자·가나 혼입"),
    (r"  *[,.?!]", "부호 앞 공백"),
    (r"[가-힣]\(", "조사 없는 괄호"),
]
lint = 0
for nid, n in nodes.items():
    texts = [n.get("text")] + [c.get("t") for c in n.get("choices", [])]
    for t in texts:
        if not t:
            continue
        for pat, label in BAD:
            if re.search(pat, t):
                warnings.append("%s %s: %s" % (nid, label, t[:44].replace("\n", " ")))
                lint += 1
    if n.get("text") and len(n["text"]) > 190:
        warnings.append("%s 긴 대사 (%d자)" % (nid, len(n["text"])))
    if n.get("who") and n["who"] not in ("나",) and n["who"] not in [h["name"] for h in meta["heroines"].values()]:
        if n["who"] in ("엘리제", "세이아"):
            errors.append("%s 화자 표기 불일치: %s" % (nid, n["who"]))

# ---------- 4. 보고 ----------
char_total = sum(len(n.get("text") or "") for n in nodes.values())
who_set = sorted({n["who"] for n in nodes.values() if n.get("who")})

print("-" * 56)
print("nodes            :", len(nodes))
print("reachable        :", len(visited))
print("explored states  :", states, "(%d steps)" % steps)
print("choice points    :", choice_nodes, "/ options:", option_count)
print("endings reached  :", ", ".join(sorted(endings_hit)))
print("max affinity     : elize %d / seia %d" % (max_aff["elize"], max_aff["seia"]))
print("characters       :", ", ".join(who_set))
print("script length    :", char_total, "chars")
print("lint warnings    :", lint)
print("-" * 56)

if warnings:
    print("\n[warnings]")
    for w in warnings[:40]:
        print(" ·", w)
    if len(warnings) > 40:
        print(" … +%d" % (len(warnings) - 40))

if errors:
    print("\n[errors]")
    for e in errors:
        print(" ✕", e)
    sys.exit(1)

print("\n✓ 구조 검사 통과 — 도달 불가 노드·끊긴 링크·막다른 길 없음")
