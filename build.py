"""data/*.json を1つの配列にまとめ，template.html に埋め込んで dist/index.html を出力する．"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
# 東京理科大は工学部 情報工学科(tus_eng.json)を使う．tus.json(創域理工学研究科)は載せない．
FILES = ["tus_eng", "isct", "utokyo", "utokyo_other", "kyoto", "osaka", "tsukuba", "nagoya", "ynu"]


def admission_for(file_adm, lab, file_name):
    adm = lab.get("admission") or None
    if adm is None and file_name == "utokyo_other":
        adm = (file_adm.get("by_senkou") or {}).get(lab.get("senkou"))
        if adm:
            adm = {**{k: v for k, v in file_adm.items() if k not in ("by_senkou", "summary", "url")}, **adm}
    if adm is None:
        adm = {k: v for k, v in file_adm.items() if k not in ("by_senkou", "guide_pdf")}
    return adm


def main():
    labs, adms, adm_index = [], [], {}
    for name in FILES:
        d = json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))
        for lab in d["labs"]:
            adm = admission_for(d.get("admission", {}), lab, name)
            key = json.dumps(adm, ensure_ascii=False, sort_keys=True)
            if key not in adm_index:
                adm_index[key] = len(adms)
                adms.append(adm)
            labs.append({
                "u": d["univ"],
                "d": lab.get("dept") or lab.get("senkou") and f"情報理工学系研究科 {lab['senkou']}専攻" or d["dept"],
                "n": lab.get("name", ""),
                "p": lab.get("prof", ""),
                "k": lab.get("kw", []),
                "t": lab.get("theme", ""),
                "l": lab.get("url", ""),
                "a": adm_index[key],
                "w": lab.get("note", ""),
                "o": lab.get("topics", []),
                "r": [[x["title"], x["year"], x.get("doi") or ""] for x in lab.get("papers", [])],
                "s": lab.get("papers_src", []),
                "c": d["checked"],
            })
    payload = "const LABS=" + json.dumps(labs, ensure_ascii=False, separators=(",", ":")) + ";\n"
    payload += "const ADM=" + json.dumps(adms, ensure_ascii=False, separators=(",", ":")) + ";"
    html = (ROOT / "template.html").read_text(encoding="utf-8").replace("/*DATA*/", payload)
    out = ROOT / "docs"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"{len(labs)} labs, {len(adms)} admission texts, {len(html)//1024} KB")


if __name__ == "__main__":
    main()
