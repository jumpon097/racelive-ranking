#!/usr/bin/env python3
"""Build a current RaceLive ranking snapshot from published HY-TEK PDFs."""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import difflib
import html.parser
import json
import os
import re
import subprocess
import tempfile
import unicodedata
import urllib.parse
import urllib.request
import urllib.error
from collections import defaultdict
from pathlib import Path


BASE_URL = "https://www.raceswim.com/racelive1/"
OUT = Path(__file__).resolve().parents[1] / "app" / "rankings.json"
CACHE_DIR = Path(os.environ["RACELIVE_CACHE_DIR"]) if os.environ.get("RACELIVE_CACHE_DIR") else None


class EventIndexParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[dict] = []
        self._current: dict | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        data = dict(attrs)
        classes = (data.get("class") or "").split()
        href = data.get("href") or ""
        if "evt-item" in classes and "has-pdf" in classes and href.endswith(".pdf"):
            self._current = {"href": href, "relay": "rel" in classes}
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._current is not None:
            label = " ".join(" ".join(self._text).split())
            match = re.match(r"(\d+)\s+(.*)", label)
            if match:
                self._current.update(event=int(match.group(1)), title=match.group(2))
                self.events.append(self._current)
            self._current = None
            self._text = []


def get_bytes(url: str, timeout: int = 45) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "RaceLive-Ranking/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def get_pdf_bytes(event: dict, timeout: int = 45) -> bytes:
    url = urllib.parse.urljoin(BASE_URL, event["href"])
    if CACHE_DIR is None:
        return get_bytes(url, timeout)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = CACHE_DIR / f"event-{event['event']}.pdf"
    meta_path = CACHE_DIR / f"event-{event['event']}.json"
    metadata = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    headers = {"User-Agent": "RaceLive-Ranking/1.0"}
    if pdf_path.exists() and metadata.get("etag"):
        headers["If-None-Match"] = metadata["etag"]
    if pdf_path.exists() and metadata.get("lastModified"):
        headers["If-Modified-Since"] = metadata["lastModified"]
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
            pdf_path.write_bytes(payload)
            meta_path.write_text(json.dumps({
                "etag": response.headers.get("ETag"),
                "lastModified": response.headers.get("Last-Modified"),
            }), encoding="utf-8")
            return payload
    except urllib.error.HTTPError as exc:
        if exc.code == 304 and pdf_path.exists():
            return pdf_path.read_bytes()
        raise


def pdf_to_text(payload: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as source:
        source.write(payload)
        source.flush()
        return subprocess.check_output(
            ["pdftotext", "-layout", source.name, "-"],
            stderr=subprocess.DEVNULL,
        ).decode("utf-8", errors="replace")


def tidy(value: str) -> str:
    value = value.replace("\x8b", "").replace("�", "")
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s+([์่้๊๋ิีึืุูัํ])", r"\1", value)
    value = re.sub(r"([เแโใไ])\s+", r"\1", value)
    value = value.replace("นํ า", "น้ำ").replace("ปั ญ", "ปัญ")
    value = value.replace("บุรรีัมย์", "บุรีรัมย์").replace("รุง่", "รุ่ง")
    return value


def normalize_team(value: str) -> str:
    value = tidy(value)
    aliases = {
        "มารียอ์ นุสรณ์": "มารีย์อนุสรณ์",
        "ี า มารียร์ักษ์ นครราชสม": "มารีย์รักษ์ นครราชสีมา",
        "ี า อนุบาลนครราชสม": "อนุบาลนครราชสีมา",
        "ิ า มหาสารคาม ตักศล": "ตักศิลามหาสารคาม",
        "ตักศลิ า มหาสารคาม": "ตักศิลามหาสารคาม",
        "ั วิชชาลัย พรชย": "พรชัยวิชชาลัย",
        "พรชยั วิชชาลัย": "พรชัยวิชชาลัย",
        "์ งหมูป่า นครวงศด": "นครวงศ์ดงหมูป่า",
        "นครวงศด์ งหมูป่า": "นครวงศ์ดงหมูป่า",
        "ั ภูมิ อะควาติกส์ ชย": "ชัยภูมิอะควาติกส์",
        "สุรนิ ทร์ สวิม": "สุรินทร์สวิม",
        "อนุบาลสุรนิ ทร์": "อนุบาลสุรินทร์",
        "มารียว์ ทิ ยา": "มารีย์วิทยา",
        "โรงเรียนแสงสุรยิ า": "โรงเรียนแสงสุริยา",
    }
    return aliases.get(value, value)


def name_fingerprint(value: str) -> str:
    tokens = []
    for token in tidy(value).split():
        cleaned = "".join(
            char for char in unicodedata.normalize("NFD", token)
            if unicodedata.category(char) != "Mn" and char.isalnum()
        )
        if cleaned:
            tokens.append(cleaned.casefold())
    return "".join(sorted(tokens))


def name_quality(value: str) -> tuple[int, int, int]:
    value = tidy(value)
    tokens = value.split()
    starts_cleanly = int(bool(value) and unicodedata.category(value[0]) != "Mn")
    natural_token_count = int(2 <= len(tokens) <= 4)
    return starts_cleanly, natural_token_count, len(value)


def classify(title: str) -> tuple[str, str]:
    lower = title.lower()
    gender = "ชาย" if re.search(r"\b(boys?|men)\b", lower) else "หญิง" if re.search(r"\b(girls?|women)\b", lower) else "ทั่วไป"
    age_match = re.search(r"(\d+)\s*(?:year olds?|&u|&o|years?)", lower)
    age_group = age_match.group(1) if age_match else "Open"
    if "& under" in lower or "&u" in lower:
        age_group += " และต่ำกว่า"
    elif "& over" in lower or "&o" in lower:
        age_group += " และสูงกว่า"
    return gender, age_group


def parse_rows(text: str, event: dict) -> list[dict]:
    rows: list[dict] = []
    lines = text.splitlines()
    header_indexes = [i for i, line in enumerate(lines) if "Rank H/R/L" in line and "Points" in line]
    for header_i in header_indexes:
        header = lines[header_i]
        relay = event["relay"]
        name_start = 15
        age_start = header.find("Age") if not relay else -1
        team_start = header.find("Team")
        finals_start = header.find("Finals")
        points_start = header.find("Points")
        if min(team_start, finals_start, points_start) < 0:
            continue
        end = next((i for i in range(header_i + 1, len(lines)) if i > header_i + 2 and ("Online results" in lines[i] or "Rank H/R/L" in lines[i])), len(lines))
        blocks: list[list[str]] = []
        current: list[str] = []
        for line in lines[header_i + 1 : end]:
            if re.match(r"^\s*\*?(?:\d+|---)\s{2,}", line):
                if current:
                    blocks.append(current)
                current = [line]
            elif current:
                current.append(line)
        if current:
            blocks.append(current)

        for block in blocks:
            first = block[0]
            rank_match = re.match(r"^\s*\*?(\d+|---)", first)
            if not rank_match or rank_match.group(1) == "---":
                continue
            rank = int(rank_match.group(1))
            clean_lines = [line for line in block if "(" not in line and not re.search(r"\b(?:DQ|NS|SCR)\b", line)]
            if relay:
                # Relay athlete details start with "1)". Only the ranked row and
                # any wrapped team-name line before that belong to the team cell.
                relay_header_lines = []
                for line in clean_lines:
                    if re.search(r"\d+\)", line):
                        break
                    relay_header_lines.append(line)
                teams = [tidy(line[name_start:65]) for line in relay_header_lines]
                team = normalize_team(" ".join(part for part in teams if part))
                name = team
                age = None
            else:
                names = [tidy(line[name_start:age_start]) for line in clean_lines]
                ages = [tidy(line[age_start:team_start]) for line in clean_lines]
                teams = [tidy(line[team_start:finals_start]) for line in clean_lines]
                name = tidy(" ".join(part for part in names if part and not re.match(r"^\d+[.:]", part)))
                age_value = next((x for x in ages if re.fullmatch(r"\d{1,2}", x)), "")
                age = int(age_value) if age_value else None
                team = normalize_team(" ".join(part for part in teams if part and not re.match(r"^\d+\)", part)))
            times = [tidy(line[finals_start:points_start]) for line in clean_lines]
            points = [tidy(line[points_start:]) for line in clean_lines]
            final_time = next((x for x in times if re.fullmatch(r"(?:\d+:)?\d{1,2}\.\d{2}", x)), "")
            point_value = next((int(x) for x in points if re.fullmatch(r"\d+", x)), 0)
            if point_value <= 0 or not team:
                continue
            gender, age_group = classify(event["title"])
            rows.append({
                "event": event["event"],
                "eventTitle": event["title"],
                "pdf": urllib.parse.urljoin(BASE_URL, event["href"]),
                "relay": relay,
                "rank": rank,
                "name": name,
                "age": age,
                "team": team,
                "time": final_time,
                "points": point_value,
                "gender": gender,
                "ageGroup": age_group,
            })
    # A multi-page event repeats headers; deduplicate by rank/name/team.
    unique = {}
    for row in rows:
        unique[(row["rank"], row["name"], row["team"])] = row
    return list(unique.values())


def fetch_event(event: dict) -> tuple[dict, list[dict], str | None]:
    error: Exception | None = None
    for _ in range(3):
        try:
            rows = parse_rows(pdf_to_text(get_pdf_bytes(event)), event)
            if rows:
                return event, rows, None
        except Exception as exc:  # Keep the snapshot useful if one event PDF is malformed.
            error = exc
    return event, [], str(error) if error else None


def main() -> None:
    parser = EventIndexParser()
    parser.feed(get_bytes(urllib.parse.urljoin(BASE_URL, "evtindex.php")).decode("utf-8", errors="replace"))
    events = parser.events
    results: list[dict] = []
    errors: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_event, event) for event in events]
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            event, rows, error = future.result()
            results.extend(rows)
            if error:
                errors.append({"event": event["event"], "error": error})
            print(f"[{index}/{len(events)}] event {event['event']}: {len(rows)} point rows", flush=True)

    athletes: dict[tuple, dict] = {}
    athlete_groups: dict[tuple, list[tuple]] = defaultdict(list)
    teams: dict[str, dict] = {}
    for row in results:
        team = teams.setdefault(row["team"], {"name": row["team"], "points": 0, "individualPoints": 0, "relayPoints": 0, "wins": 0, "podiums": 0, "athletes": set(), "events": []})
        team["points"] += row["points"]
        team["relayPoints" if row["relay"] else "individualPoints"] += row["points"]
        team["wins"] += row["rank"] == 1
        team["podiums"] += row["rank"] <= 3
        team["events"].append(row)
        if not row["relay"]:
            group_key = (row["team"], row["age"], row["gender"])
            fingerprint = name_fingerprint(row["name"])
            key = next((candidate for candidate in athlete_groups[group_key] if candidate[-1] == fingerprint), None)
            if key is None and fingerprint:
                key = next((
                    candidate for candidate in athlete_groups[group_key]
                    if difflib.SequenceMatcher(None, candidate[-1], fingerprint).ratio() >= 0.84
                ), None)
            if key is None:
                key = (*group_key, fingerprint)
                athlete_groups[group_key].append(key)
            age_group = "16+" if row["age"] is not None and row["age"] >= 16 else str(row["age"] or "ไม่ระบุ")
            athlete = athletes.setdefault(key, {"name": row["name"], "team": row["team"], "age": row["age"], "ageGroup": age_group, "gender": row["gender"], "points": 0, "wins": 0, "podiums": 0, "events": []})
            if name_quality(row["name"]) > name_quality(athlete["name"]):
                athlete["name"] = row["name"]
            athlete["points"] += row["points"]
            athlete["wins"] += row["rank"] == 1
            athlete["podiums"] += row["rank"] <= 3
            athlete["events"].append(row)
            team["athletes"].add(row["name"])

    athlete_list = sorted(athletes.values(), key=lambda x: (-x["points"], -x["wins"], x["name"]))
    team_list = sorted(teams.values(), key=lambda x: (-x["points"], -x["wins"], x["name"]))
    for index, athlete in enumerate(athlete_list, 1):
        athlete["overallRank"] = index
    age_groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for athlete in athlete_list:
        age_groups[(athlete["gender"], athlete["ageGroup"])].append(athlete)
    for members in age_groups.values():
        members.sort(key=lambda x: (-x["points"], -x["wins"], x["name"]))
        for index, athlete in enumerate(members, 1):
            athlete["ageRank"] = index
            athlete["rank"] = index
    athlete_list.sort(key=lambda x: (
        0 if x["gender"] == "ชาย" else 1,
        16 if x["ageGroup"] == "16+" else (int(x["ageGroup"]) if x["ageGroup"].isdigit() else 99),
        x["ageRank"],
    ))
    for index, team in enumerate(team_list, 1):
        team["rank"] = index
        team["athleteCount"] = len(team.pop("athletes"))

    payload = {
        "meet": {
            "name": "Northeastern Region 3 Swimming Championships",
            "nameTh": "การแข่งขันว่ายน้ำชิงชนะเลิศแห่งภาคตะวันออกเฉียงเหนือ (ภาค 3)",
            "dates": "7–9 สิงหาคม 2569",
            "status": "Unofficial",
            "source": BASE_URL,
            "generatedAt": dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(timespec="seconds"),
            "publishedEvents": len(events),
            "parsedEvents": len({row["event"] for row in results}),
            "pointRows": len(results),
            "errors": errors,
        },
        "athletes": athlete_list,
        "teams": team_list,
    }
    if OUT.exists():
        previous = json.loads(OUT.read_text(encoding="utf-8"))
        previous_without_time = json.loads(json.dumps(previous, ensure_ascii=False))
        payload_without_time = json.loads(json.dumps(payload, ensure_ascii=False))
        previous_without_time.get("meet", {}).pop("generatedAt", None)
        payload_without_time.get("meet", {}).pop("generatedAt", None)
        if previous_without_time == payload_without_time:
            payload["meet"]["generatedAt"] = previous["meet"]["generatedAt"]
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {OUT}: {len(athlete_list)} athletes, {len(team_list)} teams")


if __name__ == "__main__":
    main()
