# RaceLive Ranking

หน้าอันดับคะแนนสะสมนักกีฬาและทีมจากผลการแข่งขันที่เผยแพร่บน [RaceLive](https://www.raceswim.com/racelive1/)

## เว็บไซต์

`https://jumpon097.github.io/racelive-ranking/`

## กติกาการจัดอันดับ

- นักกีฬาแยกอันดับชาย–หญิง
- อายุ 15 ปีลงมาแยกรายอายุ
- อายุ 16 ปีขึ้นไปรวมเป็นรุ่นเดียว
- คะแนนนักกีฬาใช้เฉพาะรายการเดี่ยว
- คะแนนทีมรวมรายการเดี่ยวและผลัด

## การอัปเดตอัตโนมัติ

GitHub Actions ตรวจ RaceLive ทุก 15 นาที คำนวณอันดับใหม่ และ deploy GitHub Pages โดยอัตโนมัติ ดูขั้นตอนติดตั้งใน [DEPLOY-GITHUB-PAGES.md](DEPLOY-GITHUB-PAGES.md)

## สร้างเว็บในเครื่อง

```bash
npm ci
npm run build:github
```

ไฟล์เว็บจะอยู่ใน `github-pages-dist`
