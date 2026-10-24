import json, os, sys


def stamp(sec):
    sec = int(sec)
    return f"{sec // 60:02d}:{sec % 60:02d}"


def main():
    spec_path = sys.argv[1]
    spec = json.load(open(spec_path))
    build = os.path.join("build", spec["id"])
    tm = json.load(open(os.path.join(build, "timings.json")))
    pub = spec.get("publish", {})
    desc = pub.get("description", "")
    labels = pub.get("chapters", [])
    if "{chapters}" in desc:
        lines, t, last = [], 0.0, None
        for i, sc in enumerate(tm["scenes"]):
            lab = labels[i] if i < len(labels) else None
            if lab and lab != last:
                if not lines or t - lines[-1][0] >= 10:
                    lines.append((t, lab))
                last = lab
            t += sc["dur"]
        text = "\n".join(f"{stamp(a)} {b}" for a, b in lines) if len(lines) >= 3 else ""
        desc = desc.replace("{chapters}", text).replace("\n\n\n", "\n\n")
    out = {
        "title": pub.get("title", spec["id"])[:100],
        "description": desc[:4900],
        "tags": pub.get("tags", []),
        "category": pub.get("category", "EDUCATION"),
        "type": "short" if spec.get("format") == "short" else "video",
        "duration": tm["total"],
        "video": os.path.join(build, spec["id"] + ".mp4"),
        "thumb": os.path.join(build, spec["id"] + ".jpg") if os.path.exists(os.path.join(build, "thumb.jpg")) else None,
    }
    final = os.path.join(build, "final.mp4")
    if os.path.exists(final):
        os.replace(final, out["video"]) if not os.path.exists(out["video"]) else None
    if out["thumb"] and not os.path.exists(out["thumb"]):
        os.replace(os.path.join(build, "thumb.jpg"), out["thumb"])
    json.dump(out, open(os.path.join(build, "publish.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
