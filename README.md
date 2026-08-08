# RaceLive Ranking

หน้าอันดับคะแนนสะสมนักกีฬาและทีมจากผลการแข่งขันที่เผยแพร่บน [RaceLive](https://www.raceswim.com/racelive1/)

## กติกาการจัดอันดับ

- นักกีฬาแยกอันดับชาย–หญิง
- อายุ 15 ปีลงมาแยกรายอายุ
- อายุ 16 ปีขึ้นไปรวมเป็นรุ่นเดียว
- คะแนนนักกีฬาใช้เฉพาะรายการเดี่ยว ส่วนคะแนนทีมรวมรายการเดี่ยวและผลัด

## การอัปเดตอัตโนมัติ

GitHub Actions ตรวจ RaceLive ทุก 15 นาที ดาวน์โหลดเฉพาะ PDF ที่เพิ่มหรือเปลี่ยนแปลง คำนวณอันดับใหม่ และ commit `app/rankings.json` เมื่อข้อมูลเปลี่ยน เมื่อเชื่อม repository นี้กับ Cloudflare Pages การ commit จะทำให้เว็บเผยแพร่ข้อมูลใหม่อัตโนมัติ

## Cloudflare Pages

- Production branch: `main`
- Build command: `npm run build:cloudflare`
- Build output directory: `cloudflare-dist`
- Node.js: 22

สามารถสั่งอัปเดตทันทีได้ที่แท็บ **Actions** → **Update RaceLive rankings** → **Run workflow**

## พัฒนาในเครื่อง

```bash
npm ci
npm run dev
```

สร้างไฟล์สำหรับ Cloudflare Pages:

```bash
npm run build:cloudflare
```
