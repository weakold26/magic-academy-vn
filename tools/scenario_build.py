#!/usr/bin/env python3
"""시나리오 작작 DSL + JSON 빌더.

각 장 모듈은 build(S)를 노출한다. S.line()은 노드를 추가하고, 기본적으로 다음에
추가되는 노드로 이어진다. S.choice()는 직전 노드에 선택지를 붙인다. 라벨은
점프 지점을 읽기 쉽게 만들고, 마지막에 실제 노드 id로 바꾼다.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import s0_prologue, s1_hall, s2_tower, s3_greenhouse, s4_festival, s5_finale  # noqa: E402

MODULES = (s0_prologue, s1_hall, s2_tower, s3_greenhouse, s4_festival, s5_finale)


class Scene:
    def __init__(self):
        self.nodes = []
        self.labels = {}

    def line(self, text=None, who=None, e=None, bg=None, ch=None, show=None,
             hide=False, bgm=None, eff=None, ending=None, choices=None,
             show2=None, hide2=False):
        nid = "n%03d" % (len(self.nodes) + 1)
        node = {}
        if who:
            node["who"] = who
        if text:
            node["text"] = text
        if e:
            node["e"] = e
        if bg:
            node["bg"] = bg
        if ch:
            node["ch"] = ch
        if show:
            node["show"] = show
        if hide:
            node["hide"] = True
        if show2:
            node["show2"] = show2
        if hide2:
            node["hide2"] = True
        if bgm:
            node["bgm"] = bgm
        if ending:
            node["ending"] = ending
        if choices:
            node["choices"] = choices
        self.nodes.append({"id": nid, "node": node})
        return nid

    def label(self, name):
        if name in self.labels:
            raise SystemExit("duplicate label: %s" % name)
        self.labels[name] = "n%03d" % (len(self.nodes) + 1)

    def choice(self, options):
        self.nodes[-1]["node"]["choices"] = options
        return self.nodes[-1]["id"]

    def goto(self, label):
        nid = "n%03d" % (len(self.nodes) + 1)
        self.nodes.append({"id": nid, "node": {"goto": "@" + label}})
        return nid

    def branch(self, rules):
        nid = "n%03d" % (len(self.nodes) + 1)
        self.nodes.append({"id": nid, "node": {"branch": rules}})
        return nid

    def finish(self):
        out = {}
        nodes = self.nodes

        for i, item in enumerate(nodes):
            n = item["node"]
            if "goto" in n:
                n["next"] = n.pop("goto")
            if "branch" in n:
                conv = []
                for c, t in n["branch"]:
                    if c is None or c == "None":
                        conv.append({"next": "@" + t})
                    else:
                        conv.append({"if": c, "next": "@" + t})
                n["branch"] = conv
            if "choices" in n:
                for c in n["choices"]:
                    if "to" in c:
                        c["next"] = "@" + c.pop("to")
            if ("next" not in n and "choices" not in n and "branch" not in n
                    and "ending" not in n and i + 1 < len(nodes)):
                n["next"] = nodes[i + 1]["id"]

        for item in nodes:
            n = item["node"]

            def ref(v):
                if isinstance(v, str) and v.startswith("@"):
                    key = v[1:]
                    if key not in self.labels:
                        raise SystemExit("unknown label: %s" % key)
                    return self.labels[key]
                return v

            if "next" in n:
                n["next"] = ref(n["next"])
            if "branch" in n:
                for b in n["branch"]:
                    b["next"] = ref(b["next"])
            if "choices" in n:
                for c in n["choices"]:
                    c["next"] = ref(c["next"])

        meta = dict(META)
        meta["count"] = len(nodes)
        meta["start"] = nodes[0]["id"]
        meta["labelIndex"] = {v: k for k, v in self.labels.items()}
        for item in nodes:
            out[item["id"]] = item["node"]
        return {"meta": meta, "nodes": out}


META = {
    "title": "하늘에 뜬 마법학원",
    "subtitle": "특별한 마력을 가진 편입생의 첫 학기",
    "affMax": 18,
    "heroines": {
        "elize": {"name": "엘리제", "role": "성좌반 수석 · 서리 마법", "color": "#b9d4f2"},
        "seia": {"name": "세이아", "role": "치유학과 · 온실지기", "color": "#a9d6a2"},
    },
    "endings": {
        "elize_happy": {
            "no": "01", "label": "HAPPY END", "title": "서리가 녹는 자리",
            "desc": "열여덟 번째 계단에서 잡은 손. 학기마다 여섯 번의 재심사를, 이제 둘이 함께 센다.",
        },
        "elize_normal": {
            "no": "02", "label": "NORMAL END", "title": "다음 별이 뜰 때",
            "desc": "대답을 미룬 대신 약속을 남겼다. 그녀는 가지 않겠다고, 여기 있겠다고 말했다.",
        },
        "seia_happy": {
            "no": "03", "label": "HAPPY END", "title": "온실의 봄",
            "desc": "처음으로 자기 몫의 결정을 골랐다. 온실에 봄이 오고, 화분 두 개가 나란히 놓였다.",
        },
        "seia_normal": {
            "no": "04", "label": "NORMAL END", "title": "약초와 편지",
            "desc": "성녀의 길로 떠난 그녀가 한 달에 세 번 편지를 쓴다. 화분 하나는 이쪽 창가에 있다.",
        },
        "true_end": {
            "no": "05", "label": "TRUE END", "title": "별빛을 함께",
            "desc": "한 사람이 다 들면 터지고, 셋이 나누면 아무도 아프지 않다. 삼백 년 만의 첫 계약.",
        },
    },
}


def main():
    S = Scene()
    for mod in MODULES:
        mod.build(S)
    data = S.finish()
    out = os.path.join(os.path.dirname(__file__), "..", "src", "data", "scenario.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("wrote", out, len(data["nodes"]), "nodes", len(data["meta"]["endings"]), "endings")


if __name__ == "__main__":
    main()
