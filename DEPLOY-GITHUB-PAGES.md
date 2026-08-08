# วิธีติดตั้ง RaceLive Ranking บน GitHub Pages

## 1. นำไฟล์ขึ้น repository

แตก ZIP แล้วนำไฟล์ทั้งหมดภายในโฟลเดอร์ `racelive-ranking` ขึ้น repository:

`https://github.com/jumpon097/racelive-ranking`

ต้องคงโฟลเดอร์ `.github/workflows` ไว้ เพราะเป็นส่วนที่ตรวจผลและ deploy เว็บอัตโนมัติ

## 2. อนุญาตให้ Workflow บันทึกข้อมูล

เปิด repository แล้วไปที่:

**Settings → Actions → General → Workflow permissions**

เลือก **Read and write permissions** แล้วกด **Save**

## 3. เปิด GitHub Pages

ไปที่:

**Settings → Pages → Build and deployment → Source**

เลือก **GitHub Actions**

## 4. ทดสอบครั้งแรก

เปิดแท็บ **Actions** เลือก **Update rankings and deploy GitHub Pages** แล้วกด **Run workflow**

เมื่อสำเร็จ เว็บจะอยู่ที่:

`https://jumpon097.github.io/racelive-ranking/`

## การอัปเดตอัตโนมัติ

Workflow จะทำงานทุก 15 นาที โดย:

1. ตรวจรายการผลบน RaceLive
2. ดาวน์โหลดเฉพาะ PDF ที่เพิ่มหรือเปลี่ยนแปลง
3. คำนวณอันดับนักกีฬาและทีมใหม่
4. บันทึก `app/rankings.json` เฉพาะเมื่อข้อมูลเปลี่ยน
5. สร้างและ deploy GitHub Pages

หมายเหตุ: GitHub อาจเริ่มงานตามกำหนดช้ากว่าเวลาที่ตั้งไว้เล็กน้อยในช่วงที่ระบบมีงานหนาแน่น
