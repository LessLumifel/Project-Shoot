# Short Multi-Platform Uploader (Facebook / YouTube / TikTok)

โปรเจกต์ตัวอย่างสำหรับสร้างโปรแกรมที่สามารถอัปโหลดคลิปสั้นไปหลายแพลตฟอร์ม พร้อมรองรับรายละเอียดเฉพาะของแต่ละแพลตฟอร์ม

## แนวคิด

- ใช้ **ไฟล์ input เดียว** (video + metadata กลาง)
- แปลง metadata กลางเป็นรูปแบบเฉพาะแพลตฟอร์ม
- แยก uploader เป็นรายแพลตฟอร์ม (`FacebookUploader`, `YouTubeUploader`, `TikTokUploader`)
- เรียกใช้งานผ่าน CLI ด้วยคำสั่งเดียว

## โครงสร้างไฟล์

- `short_uploader.py` - CLI และ uploader logic
- `config.example.json` - ตัวอย่างการตั้งค่าช่อง/บัญชี
- `example_payload.json` - ตัวอย่างข้อมูลคลิป

## การติดตั้ง

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## วิธีใช้งาน

1. คัดลอก `config.example.json` เป็น `config.json` และใส่ token จริง
2. แก้ `example_payload.json` ให้ตรงกับคลิปจริง
3. รัน:

```bash
python short_uploader.py \
  --config config.json \
  --payload example_payload.json \
  --platforms facebook,youtube,tiktok
```

## หมายเหตุสำคัญ

โค้ดนี้เป็น **starter template**:
- endpoint จริงของแต่ละแพลตฟอร์มอาจมีหลายขั้นตอน (init upload, chunk upload, publish)
- ต้องตั้งค่า OAuth/App permissions ให้ถูกต้อง
- ควรเพิ่มระบบ retry, monitoring, และ queue ก่อนใช้งาน production
