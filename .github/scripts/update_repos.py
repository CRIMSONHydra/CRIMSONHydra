"""Rewrite the TOP_REPOS block in README.md from the owner's public repos."""
import json
import os
import re
import subprocess
import urllib.parse

OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "CRIMSONHydra")
COUNT = 6
COLORS = {
    "Python": "3776AB", "JavaScript": "F7DF1E", "TypeScript": "3178C6",
    "Java": "ED8B00", "C++": "00599C", "Go": "00ADD8", "Shell": "4EAA25",
}

raw = subprocess.check_output(
    ["gh", "api", f"users/{OWNER}/repos?per_page=100&type=owner"], text=True
)
repos = [
    r for r in json.loads(raw)
    if not r["fork"] and not r["archived"]
    and r["name"].lower() != OWNER.lower()
    and not r["name"].lower().startswith("temp")
]
# Described repos first, then stars, then most recently pushed.
repos.sort(
    key=lambda r: (bool(r["description"]), r["stargazers_count"], r["pushed_at"]),
    reverse=True,
)


def badge(label, color, logo=None):
    label = urllib.parse.quote(label.replace("-", "--"))
    url = f"https://img.shields.io/badge/{label}-{color}?style=flat-square"
    if logo:
        url += f"&logo={logo}&logoColor=white"
    return f'<img src="{url}" alt="{label}" />'


def cell(r):
    desc = r["description"] or "No description yet."
    lang = r["language"]
    tags = []
    if lang:
        tags.append(badge(lang, COLORS.get(lang, "555555")))
    tags.append(f'<img src="https://img.shields.io/github/stars/{OWNER}/{r["name"]}?style=flat-square&color=dc143c&label=%E2%98%85" alt="stars" />')
    return (
        f'    <td width="50%" valign="top">\n'
        f'      <a href="{r["html_url"]}"><b>{r["name"]}</b></a><br/>\n'
        f'      <sub>{desc}</sub><br/><br/>\n'
        f'      {" ".join(tags)}\n'
        f'    </td>'
    )


top = repos[:COUNT]
rows = []
for i in range(0, len(top), 2):
    pair = top[i:i + 2]
    cells = [cell(r) for r in pair]
    if len(cells) == 1:
        cells.append('    <td width="50%"></td>')
    rows.append("  <tr>\n" + "\n".join(cells) + "\n  </tr>")
table = "<table>\n" + "\n".join(rows) + "\n</table>"

text = open("README.md", encoding="utf-8").read()
new = re.sub(
    r"(<!-- TOP_REPOS:START -->).*?(<!-- TOP_REPOS:END -->)",
    lambda m: f"{m.group(1)}\n{table}\n{m.group(2)}",
    text,
    flags=re.S,
)
open("README.md", "w", encoding="utf-8").write(new)
