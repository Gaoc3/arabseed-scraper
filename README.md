# 🎬 كاشف ومستخرج روابط عرب سيد الاحترافي (ArabSeed Scraper & Decrypter API)

أداة بايثون (Python) متطورة وسريعة جداً للبحث التفاعلي واستخراج جميع روابط **المشاهدة المباشرة (البث المباشر)** وروابط **التحميل المباشر** من موقع عرب سيد ومراياه المختلفة وفك تشفيرها تلقائياً.

[![Docs](https://img.shields.io/badge/Documentation-GitHub%20Pages-brightgreen?style=for-the-badge&logo=github&logoColor=white&labelColor=13101b&color=ff007f)](https://user.github.io/arabseed-scraper/)
[![PyPI](https://img.shields.io/badge/PyPI-v1.0.0-blue?style=for-the-badge&logo=pypi&logoColor=white&labelColor=13101b&color=00f0ff)](https://pypi.org/project/arabseed-scraper/)

---

## ✨ المميزات الرئيسية (Key Features)

1. **فك التشفير الكامل (100% Decryption)**: يقوم الكود تلقائياً باكتشاف وفك تشفير الروابط المبهمة والمحمية بـ Base64 ليوفر لك الروابط المباشرة والسريعة فوراً.
2. **استخراج المشاهدة والتحميل معاً**: يستخرج جميع سيرفرات البث المباشر (مثل مشغل عرب سيد المدمج) بالإضافة إلى جميع سيرفرات التحميل بمختلف الجودات والأحجام.
3. **دعم كامل للمسلسلات**: عند اختيار مسلسل، يكتشف السكريبت قائمة حلقات الموسم بالكامل، ويعرضها لك بشكل تفاعلي لتختار الحلقة المطلوبة.
4. **تخطي الحجب التلقائي (Automatic Fallback)**: في حال تم حجب النطاق الرئيسي في بلدك، يقوم الكود تلقائياً بالتبديل بين النطاقات البديلة الشغالة (Mirrors) لضمان استقرار العمل.
5. **واجهتين للتشغيل (Dual Interface)**:
   - **واجهة برمجية (API Class)**: سهلة الدمج في أي مشروع بايثون آخر أو سيرفر ويب (FastAPI / Flask).
   - **واجهة تفاعلية (CLI)**: واجهة رسومية ملونة ومنظمة داخل مبسط الأوامر باستخدام مكتبة `rich`.

---

## 🛠️ كيفية التثبيت والتشغيل (Installation & Setup)

### 1. تثبيت المتطلبات (Install Dependencies)
افتح مبسط الأوامر (Terminal/CMD) في هذا المجلد وقم بتثبيت المكتبات المطلوبة:
```bash
pip install -r requirements.txt
```

### 2. تشغيل الأداة التفاعلية (Run the CLI Tool)
لتشغيل واجهة البحث والتحميل التفاعلية الرائعة:
```bash
python arabseed_scraper.py
```

---

## 📦 استخدام الكود برمجياً (API Integration)

يمكنك استيراد الكود واستخدامه في مشروعك الخاص بكل سهولة:

```python
from arabseed_scraper import ArabSeedAPI

# 1. تهيئة الكلاس
api = ArabSeedAPI()

# 2. البحث عن فيلم أو مسلسل أو أغنية
results = api.search("فيلم الست")

for idx, item in enumerate(results):
    print(f"[{idx}] {item['title']} - النوع: {item['type']}")

# 3. استخراج روابط المشاهدة والتحميل لأول نتيجة
if results:
    url = results[0]['url']
    
    print("\n📺 سيرفرات البث المباشر (Streaming):")
    watch_links = api.get_watch_links(url)
    for w in watch_links:
        print(f"  السيرفر: {w['server']} -> رابط البث: {w['direct_link']}")
        
    print("\n📥 سيرفرات التحميل المباشر (Downloads):")
    download_links = api.get_download_links(url)
    for d in download_links:
        print(f"  السيرفر: {d['server']} | الجودة: {d['quality']} -> الرابط: {d['direct_link']}")
```

---

## 👨‍💻 معلومات النقل والمسارات
* **المسار الحالي للمشروع المكتمل**: `C:\Users\secon\Documents\ArabSeedScraper\`
* **الملف الرئيسي**: `arabseed_scraper.py`
* **ملف المتطلبات**: `requirements.txt`
