# วิธีนำขึ้น GitHub และ Cloudflare Pages

## แบบที่แนะนำ: GitHub + อัปเดตอัตโนมัติ

1. แตกไฟล์ ZIP แล้วนำไฟล์ทั้งหมดภายในโฟลเดอร์ `racelive-ranking` ขึ้น repository `jumpon097/racelive-ranking` โดยต้องคงโฟลเดอร์ `.github/workflows` ไว้
2. ใน GitHub เปิด **Settings → Actions → General → Workflow permissions** แล้วเลือก **Read and write permissions**
3. เชื่อม repository กับ Cloudflare Pages โดยกำหนด:
   - Production branch: `main`
   - Build command: `npm run build:cloudflare`
   - Build output directory: `cloudflare-dist`
   - Node.js version: `22`
4. เปิดแท็บ **Actions** ใน GitHub เลือก **Update RaceLive rankings** แล้วกด **Run workflow** เพื่อทดสอบครั้งแรก

หลังตั้งค่าแล้ว GitHub Actions จะตรวจ RaceLive ทุก 15 นาที หากผลเปลี่ยน ระบบจะคำนวณอันดับและ commit ข้อมูลใหม่ ทำให้ Cloudflare Pages deploy เวอร์ชันใหม่อัตโนมัติ

## แบบ Direct Upload

อัปโหลดไฟล์ภายในโฟลเดอร์ `direct-upload` ไปยัง Cloudflare Pages ได้ทันที แต่แบบนี้จะ **ไม่อัปเดตอัตโนมัติ** เพราะไม่ได้เชื่อมกับ GitHub Actions

## กติกาอันดับนักกีฬา

- แยกชายและหญิง
- อายุ 15 ปีลงมาแยกรายอายุ
- อายุ 16 ปีขึ้นไปรวมเป็นรุ่นเดียว
