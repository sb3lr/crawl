import os  # بنستخدم مكتبة os عشان نقدر نتعامل مع نظام التشغيل، زي إنشاء مجلدات وملفات
import subprocess  # مكتبة مهمة عشان نقدر نشغّل أوامر خارجية من بايثون، مثل أمر gospider
import time  # بنستخدمها عشان نوقف السكريبت لفترة معينة (تأخير)
import random  # مكتبة بتطلع لنا أرقام عشوائية، عشان نخلي التأخير غير ثابت
import re  # مكتبة التعامل مع التعبيرات المنتظمة (Regular Expressions) اللي بنستخدمها للفلترة

# ===== إعدادات أساسية =====
SUBS_FILE = "httpx.txt"  # اسم الملف اللي فيه كل الـ subdomains
OUTPUT_DIR = "output"  # اسم المجلد اللي بنحفظ فيه كل النتائج
RAW_OUTPUT = os.path.join(OUTPUT_DIR, "gospider_all.txt")  # مسار الملف اللي بنحط فيه كل نتائج gospider
ALL_URLS = os.path.join(OUTPUT_DIR, "all_urls.txt")  # مسار الملف اللي فيه كل الروابط اللي لقيناها
PARAM_URLS = os.path.join(OUTPUT_DIR, "urls_with_params.txt")  # مسار الملف اللي فيه الروابط اللي لها "parameters"
PARAM_NAMES = os.path.join(OUTPUT_DIR, "param_names.txt")  # مسار الملف اللي فيه أسماء الـ parameters بس
SENSITIVE_PATHS = os.path.join(OUTPUT_DIR, "sensitive_paths.txt")  # مسار الملف اللي فيه المسارات المهمة

# بنتحقق إذا مجلد النتائج موجود أو لا، وإذا مو موجود، بنسويه
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ===== تحقق من وجود gospider =====
try:
    # بنحاول نشغّل gospider عشان نتأكد إنه مثبت. -h بيطلع المساعدة بسرعة
    # stdout و stderr بنخليهم يروحون لمكان فاضي عشان ما نشوف المخرجات على الشاشة
    subprocess.run(["gospider", "-h"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except FileNotFoundError:
    # إذا الأمر ما اشتغل (يعني gospider مو موجود)، بتطلع لنا هذي الرسالة
    print("[!] gospider غير مثبت. الرجاء تثبيته أولاً:")
    print("go install github.com/jaeles-project/gospider@latest")
    exit(1) # ونوقف تشغيل السكريبت

# ===== تحقق من ملف الـ subdomains =====
# بنشوف إذا ملف النطاقات موجود
if not os.path.exists(SUBS_FILE):
    print(f"[!] ملف {SUBS_FILE} غير موجود.") # إذا مو موجود، نطبع رسالة ونوقف
    exit(1)

# بنفتح ملف النتائج الرئيسي ونمسح كل شيء فيه قبل ما نبدأ عشان ما تتلخبط النتائج
with open(RAW_OUTPUT, 'w') as f:
    f.write('')

# ===== حلقة الزحف على كل subdomain =====
# بنفتح ملف النطاقات للقراءة
with open(SUBS_FILE, 'r') as subs_file:
    # بنقرأ كل سطر في الملف وبنحطه في قائمة (list) وبنشيل الفراغات الزايدة
    subdomains = [line.strip() for line in subs_file if line.strip()]

# بنمشي على كل subdomain في القائمة واحد واحد
for sub in subdomains:
    print(f"[*] الزحف على https://{sub} ...") # نطبع رسالة عشان نعرف وش قاعد يصير

    # بنبني الأمر اللي بنشغله في الطرفية (terminal)
    cmd = ["gospider", "-s", f"https://{sub}", "-c", "2", "-d", "2", "-t", "10", "-a", "-r"]

    # بنشغل الأمر
    try:
        # subprocess.run بتشغل الأمر، capture_output=True يعني احفظ المخرجات في متغير
        process = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # بنفتح ملف النتائج عشان نضيف عليه
        with open(RAW_OUTPUT, 'a') as f:
            # بنضيف المخرجات العادية (اللي هي النتائج)
            f.write(process.stdout)
            # وبنضيف مخرجات الخطأ كمان (عشان ما نضيع أي شيء)
            f.write(process.stderr)
    except subprocess.CalledProcessError as e:
        # لو صار أي خطأ أثناء تشغيل gospider (مثلاً الموقع ما فتح)، بنطبع رسالة ونكمل
        print(f"[!] حدث خطأ أثناء الزحف على {sub}: {e}")

    # بنوقف السكريبت لمدة عشوائية بين 1 و 2 ثانية عشان ما يكتشفنا الموقع وننحظر
    time.sleep(random.uniform(1, 2))

print(f"[*] الزحف على كل subdomain مكتمل. النتائج في {RAW_OUTPUT}")

# ===== فلترة النتائج =====
print("[*] بدء فلترة النتائج...")

# بنفتح الملف اللي فيه كل النتائج اللي جمعناها
with open(RAW_OUTPUT, 'r') as f:
    raw_content = f.read() # بنقرأ كل محتوى الملف ونحطه في متغير

# بنبحث عن كل الروابط (URLs) في المحتوى باستخدام "تعبير منتظم"
all_urls_list = sorted(list(set(re.findall(r'https?://[^ ]+', raw_content))))
# بنحفظ الروابط اللي لقيناها في ملف جديد
with open(ALL_URLS, 'w') as f:
    f.write('\n'.join(all_urls_list))

# بنشوف أي رابط فيه علامة استفهام (=?) عشان نعرف إنه فيه parameters
param_urls_list = [url for url in all_urls_list if '?' in url and '=' in url]
# بنحفظ هذي الروابط في ملف ثاني
with open(PARAM_URLS, 'w') as f:
    f.write('\n'.join(param_urls_list))

# بنبدأ نجمع أسماء الـ parameters
param_names_set = set() # بنستخدم set عشان ما تتكرر الأسماء
for url in param_urls_list:
    # بنقسم الرابط من عند علامة الاستفهام عشان ناخذ الجزء اللي بعده
    query_string = url.split('?', 1)[1]
    # لو كان فيه علامة # بنشيلها مع كل شيء بعدها
    if '#' in query_string:
        query_string = query_string.split('#', 1)[0]

    # بنقسم الـ parameters من عند علامة &
    params = query_string.split('&')
    for param in params:
        # بنقسم كل parameter من عند = عشان ناخذ اسمه
        param_name = param.split('=', 1)[0]
        param_names_set.add(param_name) # وبنضيفه على الـ set

param_names_list = sorted(list(param_names_set)) # بنحول الـ set إلى list وبنرتبهم
# بنحفظ أسماء الـ parameters في ملف خاص
with open(PARAM_NAMES, 'w') as f:
    f.write('\n'.join(param_names_list))

# بنبحث عن المسارات الحساسة باستخدام تعبير منتظم (مثل /admin, /login, إلخ)
sensitive_patterns = r'/admin|/login|/api|/dashboard|/config|\.env|\.php|/wp-'
sensitive_paths_list = [url for url in all_urls_list if re.search(sensitive_patterns, url)]
# بنحفظ هذي المسارات في ملف منفصل
with open(SENSITIVE_PATHS, 'w') as f:
    f.write('\n'.join(sensitive_paths_list))

# في النهاية، بنطبع رسالة عشان نعرف مكان الملفات
print("[*] جميع URLs الحية:", ALL_URLS)
print("[*] URLs التي تحتوي GET parameters:", PARAM_URLS)
print("[*] أسماء الـ GET parameters فقط:", PARAM_NAMES)
print("[*] المسارات الحساسة والمهمة:", SENSITIVE_PATHS)
print("[*] جاهز للاستخدام لاحقًا في Burp Intruder/Scanner.")
