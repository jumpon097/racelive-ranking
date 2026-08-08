"use client";

import { useMemo, useState } from "react";

type ResultEvent = {
  event: number;
  eventTitle: string;
  pdf: string;
  relay: boolean;
  rank: number;
  points: number;
  time: string;
};

type Athlete = {
  rank: number;
  ageRank: number;
  overallRank: number;
  name: string;
  team: string;
  age: number | null;
  ageGroup: string;
  gender: string;
  points: number;
  wins: number;
  podiums: number;
  events: ResultEvent[];
};

type Team = {
  rank: number;
  name: string;
  points: number;
  individualPoints: number;
  relayPoints: number;
  wins: number;
  podiums: number;
  athleteCount: number;
  events: ResultEvent[];
};

type RankingData = {
  meet: {
    nameTh: string;
    dates: string;
    status: string;
    source: string;
    generatedAt: string;
    publishedEvents: number;
    parsedEvents: number;
    pointRows: number;
  };
  athletes: Athlete[];
  teams: Team[];
};

const medals = ["ทอง", "เงิน", "ทองแดง"];

function dateTimeThai(value: string) {
  return new Intl.DateTimeFormat("th-TH", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Asia/Bangkok",
  }).format(new Date(value));
}

function podiumLabel(rank: number) {
  return rank <= 3 ? medals[rank - 1] : `อันดับ ${rank}`;
}

export default function RankingClient({ data }: { data: RankingData }) {
  const [tab, setTab] = useState<"athletes" | "teams">("athletes");
  const [query, setQuery] = useState("");
  const [gender, setGender] = useState("ทั้งหมด");
  const [age, setAge] = useState("ทั้งหมด");
  const [expanded, setExpanded] = useState<string | null>(null);

  const ageGroups = useMemo(
    () => Array.from(new Set(data.athletes.map((item) => item.ageGroup))).sort((a, b) => {
      const ageA = a === "16+" ? 16 : Number(a);
      const ageB = b === "16+" ? 16 : Number(b);
      return ageA - ageB;
    }),
    [data.athletes],
  );

  const ageGroupLabel = (value: string) => value === "16+" ? "16 ปีขึ้นไป" : `${value} ปี`;

  const athletes = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase("th");
    return data.athletes.filter(
      (item) =>
        (gender === "ทั้งหมด" || item.gender === gender) &&
        (age === "ทั้งหมด" || item.ageGroup === age) &&
        (!needle || `${item.name} ${item.team}`.toLocaleLowerCase("th").includes(needle)),
    );
  }, [age, data.athletes, gender, query]);

  const teams = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase("th");
    return data.teams.filter(
      (item) => !needle || item.name.toLocaleLowerCase("th").includes(needle),
    );
  }, [data.teams, query]);

  const visible = tab === "athletes" ? athletes : teams;
  const showAthletePodium = tab === "athletes" && gender !== "ทั้งหมด" && age !== "ทั้งหมด";
  const leaders = (tab === "teams" || showAthletePodium) ? visible.slice(0, 3) : [];

  return (
    <main>
      <header className="hero">
        <nav className="topbar" aria-label="เมนูหลัก">
          <a className="brand" href="#top" aria-label="RaceLive Ranking หน้าหลัก">
            <span className="brandMark">R</span>
            <span>RaceLive <strong>Ranking</strong></span>
          </a>
          <a className="sourceButton" href={data.meet.source} target="_blank" rel="noreferrer">
            ดูผลการแข่งขันต้นฉบับ <span aria-hidden="true">↗</span>
          </a>
        </nav>

        <section className="heroContent" id="top">
          <div>
            <p className="eyebrow"><span className="liveDot" /> UNOFFICIAL LIVE RESULTS</p>
            <h1>อันดับนักกีฬา<br /><span>และทีมว่ายน้ำ</span></h1>
            <p className="meetName">{data.meet.nameTh}</p>
            <div className="meetMeta">
              <span>{data.meet.dates}</span>
              <span>อัปเดต {dateTimeThai(data.meet.generatedAt)} น.</span>
            </div>
          </div>
          <div className="scoreCard" aria-label="ความคืบหน้าผลการแข่งขัน">
            <p>ผลที่ประกาศแล้ว</p>
            <strong>{data.meet.publishedEvents}<small> / 218</small></strong>
            <div className="progress"><span style={{ width: `${(data.meet.publishedEvents / 218) * 100}%` }} /></div>
            <div className="scoreFacts">
              <span><b>{data.athletes.length}</b> นักกีฬาได้คะแนน</span>
              <span><b>{data.teams.length}</b> ทีม</span>
            </div>
          </div>
        </section>
      </header>

      <section className="workspace" aria-label="ตารางอันดับ">
        <div className="tabs" role="tablist">
          <button className={tab === "athletes" ? "active" : ""} onClick={() => { setTab("athletes"); setExpanded(null); }} role="tab" aria-selected={tab === "athletes"}>
            อันดับนักกีฬา <span>{data.athletes.length}</span>
          </button>
          <button className={tab === "teams" ? "active" : ""} onClick={() => { setTab("teams"); setExpanded(null); }} role="tab" aria-selected={tab === "teams"}>
            อันดับทีม <span>{data.teams.length}</span>
          </button>
        </div>

        <div className="filters">
          <label className="searchBox">
            <span aria-hidden="true">⌕</span>
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={tab === "athletes" ? "ค้นหาชื่อนักกีฬา หรือทีม…" : "ค้นหาชื่อทีม…"} />
            {query && <button onClick={() => setQuery("")} aria-label="ล้างคำค้นหา">×</button>}
          </label>
          {tab === "athletes" && <div className="athleteFilters">
            <div className="segmented" aria-label="กรองเพศ">
              {["ทั้งหมด", "ชาย", "หญิง"].map((item) => (
                <button key={item} className={gender === item ? "active" : ""} onClick={() => setGender(item)}>{item}</button>
              ))}
            </div>
            <label className="ageSelect">รุ่นอายุ
              <select value={age} onChange={(event) => setAge(event.target.value)}>
                <option value="ทั้งหมด">ทั้งหมด</option>
                {ageGroups.map((item) => <option value={item} key={item}>{ageGroupLabel(item)}</option>)}
              </select>
            </label>
          </div>}
        </div>

        {!query && (tab === "teams" || showAthletePodium) && (
          <div className="podium">
            {leaders.map((item, index) => (
              <article className={`podiumCard place${index + 1}`} key={"name" in item ? `${item.name}-${item.rank}` : item.rank}>
                <div className="medal">{index + 1}</div>
                <p>{podiumLabel(index + 1)}</p>
                <h2>{item.name}</h2>
                {"team" in item && <span>{item.team}</span>}
                <strong>{item.points} <small>คะแนน</small></strong>
                <div className="miniStats">
                  <span>ชนะ <b>{item.wins}</b></span>
                  <span>โพเดียม <b>{item.podiums}</b></span>
                </div>
              </article>
            ))}
          </div>
        )}

        <div className="tableCard">
          <div className="tableHeader">
            <div>
              <p>{tab === "athletes" ? "AGE GROUP HIGH POINT" : "TEAM POINTS"}</p>
              <h2>{tab === "athletes" ? `อันดับนักกีฬาแยกตามรุ่นอายุ${age !== "ทั้งหมด" ? ` ${ageGroupLabel(age)}` : ""}${gender !== "ทั้งหมด" ? ` · ${gender}` : ""}` : "อันดับคะแนนสะสมทีม"}</h2>
            </div>
            <span>พบ {visible.length.toLocaleString("th-TH")} รายการ</span>
          </div>

          <div className="rankList">
            {visible.map((item, index) => {
              const key = `${tab}-${item.rank}-${item.name}`;
              const isOpen = expanded === key;
              return (
                <article className={`rankRow ${isOpen ? "open" : ""}`} key={key}>
                  <button className="rankMain" onClick={() => setExpanded(isOpen ? null : key)} aria-expanded={isOpen}>
                    <span className={`rankNumber ${item.rank <= 3 ? `top${item.rank}` : ""}`}>{item.rank}</span>
                    <span className="identity">
                      <strong>{item.name}</strong>
                      {"team" in item ? <small>รุ่น{item.gender} {ageGroupLabel(item.ageGroup)}{item.ageGroup === "16+" ? ` · อายุ ${item.age ?? "–"} ปี` : ""} · {item.team} · อันดับรวม {item.overallRank}</small> : <small>{item.athleteCount} นักกีฬา · คะแนนเดี่ยว {item.individualPoints} · ผลัด {item.relayPoints}</small>}
                    </span>
                    <span className="badges">
                      <small>{item.wins} ชนะ</small>
                      <small>{item.podiums} โพเดียม</small>
                    </span>
                    <span className="points"><strong>{item.points}</strong><small>คะแนน</small></span>
                    <span className="chevron" aria-hidden="true">⌄</span>
                  </button>
                  {isOpen && (
                    <div className="eventDetails">
                      <p>รายการที่ได้คะแนน</p>
                      <div className="eventGrid">
                        {item.events.slice().sort((a, b) => a.event - b.event).map((event) => (
                          <a href={event.pdf} target="_blank" rel="noreferrer" key={`${event.event}-${event.rank}-${event.eventTitle}`}>
                            <span>Event {event.event}</span>
                            <strong>{event.eventTitle}</strong>
                            <small>อันดับ {event.rank} · {event.time || "–"} · +{event.points} คะแนน {event.relay ? "· ผลัด" : ""}</small>
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </article>
              );
            })}
            {visible.length === 0 && <div className="empty">ไม่พบข้อมูลที่ตรงกับคำค้นหา</div>}
          </div>
        </div>

        <aside className="methodNote">
          <strong>วิธีคิดคะแนน</strong>
          <p>นักกีฬาจัดอันดับแยกชาย–หญิง อายุ 15 ปีลงมาแยกรายอายุ ส่วนอายุ 16 ปีขึ้นไปจัดอันดับรวมในรุ่นเดียว โดยนับเฉพาะคะแนนรายการเดี่ยวตามคอลัมน์ Points ในผล HY-TEK ส่วนทีมรวมคะแนนรายการเดี่ยวและผลัด อันดับยังไม่เป็นทางการและจะเปลี่ยนเมื่อมีผลใหม่</p>
        </aside>
      </section>

      <footer>
        <span>RaceLive Ranking · สรุปจากผลการแข่งขันที่เผยแพร่</span>
        <a href={data.meet.source} target="_blank" rel="noreferrer">raceswim.com/racelive1 ↗</a>
      </footer>
    </main>
  );
}
