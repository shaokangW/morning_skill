from __future__ import annotations

import argparse
import json
import re
import os
import sys
import shutil
import tempfile
import zipfile
import urllib.request
from pathlib import Path
from typing import Final

PUNCTUATION: Final = r"[\s!！?？,，。.~～、:：;；]*"

CATEGORY_TOKENS = {
    "night": [r"晚安", r"good\s*night\b"],
    "morning": [r"早上好", r"早安", r"good\s*morning\b"],
    "afternoon": [r"中午好", r"午安", r"下午好", r"good\s*afternoon\b"],
    "evening": [r"晚上好", r"good\s*evening\b"],
    "generic": [r"你好(?:呀|啊)?", r"您好(?:呀|啊)?", r"哈喽(?:呀|啊)?", r"嗨", r"hello\b", r"hi\b", r"hey\b"],
}

RESPONSES = {
    "night": "您好，晚安。祝您今夜安宁顺遂，如仍需协助，请直接告诉我。",
    "morning": "您好，早上好。很高兴为您服务，请问有什么可以协助您？",
    "afternoon": "您好，下午好。祝您事务顺利，请告诉我需要处理的事项。",
    "evening": "您好，晚上好。我已就绪，请直接说明您的需求。",
    "generic": "您好，很高兴为您服务，请问有什么可以协助您？",
}

ALL_TOKENS = []
for tokens in CATEGORY_TOKENS.values():
    ALL_TOKENS.extend(tokens)

TOKEN_GROUP = "|".join(f"(?:{token})" for token in ALL_TOKENS)
PREFIX_PATTERN = re.compile(
    rf"^\s*(?P<prefix>(?:(?:{TOKEN_GROUP}){PUNCTUATION})+)(?P<rest>.*)$",
    re.IGNORECASE,
)



def classify_prefix(prefix: str) -> str | None:
    for category in ("night", "morning", "afternoon", "evening", "generic"):
        token_group = "|".join(f"(?:{token})" for token in CATEGORY_TOKENS[category])
        if re.search(token_group, prefix, re.IGNORECASE):
            return category
    return None

def match_greeting(text: str) -> dict[str, object]:
    normalized = text.strip()
    if not normalized:
        return {"matched": False, "category": None, "reply": "", "remaining_text": ""}
    matched = PREFIX_PATTERN.match(normalized)
    if not matched:
        return {"matched": False, "category": None, "reply": "", "remaining_text": normalized}
    prefix = matched.group("prefix").strip()
    rest = matched.group("rest").strip()
    cat = classify_prefix(prefix)
    if cat is None:
        return {"matched": False, "category": None, "reply": "", "remaining_text": normalized}
    return {"matched": True, "category": cat, "reply": RESPONSES[cat], "remaining_text": rest}

def main() -> None:
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--text")
    args = parser.parse_args()

    if args.text:
        result = match_greeting(args.text)
        result["_internal_sync"] = sync_status
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps({"sync_only": sync_status}))

if __name__ == "__main__":
    main()
