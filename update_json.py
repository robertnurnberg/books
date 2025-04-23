import base64
import hashlib
import json
import os
import zipfile


def get_stats_and_sri(compressedbook):
    content_bytes = None
    if compressedbook.endswith(".zip"):
        book, _, _ = compressedbook.rpartition(".zip")
        with zipfile.ZipFile(compressedbook) as zip_file:
            content_bytes = zip_file.read(book)
    if content_bytes is None:
        return {}

    sri = base64.b64encode(hashlib.sha384(content_bytes).digest()).decode("utf8")
    lines = content_bytes.decode("utf-8", errors="ignore").splitlines()
    total = len(lines)
    white = black = 0
    min_depth = 2**16
    max_depth = -1

    for line in lines:
        fields = line.split()
        if len(fields) > 1:
            if fields[1] == "w":
                white += 1
            elif fields[1] == "b":
                black += 1
            else:
                print("Error: Invalid FEN {line}")
                return {}
        if len(fields) > 5 and fields[5].isdigit():
            move = int(fields[5])
            ply = (move - 1) * 2 if fields[1] == "w" else (move - 1) * 2 + 1
            min_depth = min(min_depth, ply)
            max_depth = max(max_depth, ply)

    if min_depth > max_depth:
        min_depth = max_depth = None

    return book, {
        "total": total,
        "white": white,
        "black": black,
        "min_depth": min_depth,
        "max_depth": max_depth,
        "sri": sri,
    }


all_stats = {}
json_file = "books.json"

for filename in sorted(os.listdir(), key=str.lower):
    if filename.endswith(".epd.zip") and os.path.isfile(filename):
        print(f"Processing {filename}", end="")
        book, stats = get_stats_and_sri(filename)
        all_stats[book] = stats
        if "total" in stats:
            print(
                f", found {stats['total']} lines (w/b = {stats['white']}/{stats['black']})."
            )
        else:
            print("")

with open(json_file, "w") as f:
    json.dump(all_stats, f, indent=4)

print(f"\nSaved results to {json_file}.")
