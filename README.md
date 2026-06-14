# -*- coding: utf-8 -*-
# ======================================================================================================================
# 💎 MOROIA REVOLUTION ENGINE v4.0.0 - FULL ARCHITECTURE & DEPLOYMENT BLUEPRINT (الشرح البرمجي والتشريح الهندسي المتكامل)
# ======================================================================================================================
# تبدأ الأداة باستدعاء المكتبات الأساسية لضمان أعلى كفاءة تشغيلية. نستخدم مكتبة os للتعامل مع بيئة نظام التشغيل والمسارات،
# ومكتبة sys للتحكم في مخرجات المصنفة والخروج الآمن، ومكتبة time لحساب الفوارق الزمنية وإدارة معدل التحديث السريع،
# ومكتبة socket لفتح قنوات الاتصال المحلية وفلترتها، ومكتبة shutil لإدارة وحذف مجلدات الكاش بشكل كامل نهائي من الجذور،
# ومكتبة subprocess لتنفيذ أوامر سطر الأوامر منخفضة المستوى مثل استعلامات WMIC لقراءة كرت الشاشة بدقة متناهية على ويندوز،
# ومكتبة requests للاتصال الخارجي غير الحاصِر بجلب الـ IP وفحص تحديثات مستودعات PyPI الرسمية لحظر النسخ القديمة والميتة،
# ومكتبة json لمعالجة ملفات الإعدادات، ومكتبة platform لتحديد نوع النواة، ومكتبة gettext المدمجة لإدارة الترجمة الفورية،
# مع استخدام الـ datetime والـ timedelta لإدارة فترات الفحص الزمني، والـ deque لتخزين سلاسل البيانات التاريخية للاستهلاك.
# نقوم بعمل بلوكات try-except مرنة لاستيراد مكتبة psutil الخارجية؛ فإذا لم تكن مثبتة، يتم تعيين قيمتها إلى None لمنع الانهيار.

import os
import sys
import time
import socket
import shutil
import subprocess
import requests
import json
import platform
import gettext
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Optional, Tuple, Any

try:
    import psutil
except ImportError:
    psutil = None

VERSION = "4.0.0"
BUILD_DATE = "2026-06-14"

# بعد ذلك مباشرة، نقوم ببناء كلاس الألوان Colors الذي يحاكي فلسفة التصميم الحديثة وتأثيرات الـ Glassmorphism والـ Minimalist
# المميزة عبر صبغة الـ Hex Palette الفريدة وهي لغة اللون الأزرق الرمادي الناعم C8D6E0؛ يتم ذلك برمجياً عبر حقن تتابعات الهروب
# من نوع ANSI وتحديداً الـ TrueColor RGB bytes باستخدام التتابع الخطي المباشر \033[38;2;200;214;224m والذي يقوم بإعادة برمجة مخرجات
# الـ Terminal لتعرض الألوان بنقاء فائق وتناسق هندسي مريح للعين، مضافاً إليها الألوان القياسية من Cyan، Green، Warning، Fail،
# مع تتابعات حاسمة مثل CLEAR_SCREEN لمسح الشاشة وإعادة تعيين الحقول، وHIDE_CURSOR لإخفاء مؤشر الكتابة الوامض أثناء البث الحي.

class Colors:
    MAIN_THEME = '\033[38;2;200;214;224m' 
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    CLEAR_SCREEN = '\033[2J\033[H'
    HIDE_CURSOR = '\033[?25l'
    SHOW_CURSOR = '\033[?25h'

# ## 📈 SECTION 2: METRICS & HISTORICAL QUEUES (محرك قياس الأداء والسلاسل الزمنية وتجنب تسريب الذاكرة العشوائية للنظام)
# ---
# في هذا الجزء نقوم بتشريح كلاس PerformanceMonitor وهو المسؤول عن تتبع السلوك الزمني والنبض الداخلي لموارد الجهاز بالملي ثانية.
# يتم عند استدعاء دالة البناء __init__ إنشاء طوابير ثنائية النهاية deque مخصصة للذاكرة العشوائية والمعالج، مع تحديد حجم أقصى
# ثابت لها max_history=60 لضمان الاحتفاظ بآخر دقيقة تشغيلية فقط وتجنب أي استهلاك متزايد لموارد الذاكرة (Memory Leak).
# كما نقوم بالتقاط الطابع الزمني البدئي عبر دالة time.time() لتحديد نقطة انطلاق المحرك الحية. تحتوي الدالة التشغيلية update
# على فحص ذكي للـ psutil؛ فإذا كانت متوفرة، تقوم الأداة بسحب نسب الاستهلاك الحالية بدون إيقاف خيط المعالجة الرئيسي وحقنها.
# أما دالة get_uptime_string فتقوم بعملية حسابية رياضية بحتة، حيث تطرح وقت البدء من الوقت الحالي لإنتاج الفارق الإجمالي،
# ثم تقسم الفائض برمجياً عبر لغاريتمات الحساب القياسي لمعرفة عدد الساعات, الدقائق، والثواني المنقضية بدقة تامة وبدون أي تذبذب.

class PerformanceMonitor:
    def __init__(self, max_history=60):
        self.cpu_history = deque(maxlen=max_history)
        self.ram_history = deque(maxlen=max_history)
        self.start_time = time.time()
        
    def update(self):
        if psutil:
            self.cpu_history.append(psutil.cpu_percent(interval=None))
            self.ram_history.append(psutil.virtual_memory().percent)
    
    def get_uptime_string(self):
        uptime = int(time.time() - self.start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# ## ⚙️ SECTION 3: CORE LOGIC INITIALIZATION & LOCALIZATION (نواة المحرك وإدارة التوطين والترجمة والملفات الخفية)
# ---
# هنا نصل إلى قلب المحرك النابض كلاس MoroiaEngine. في دالة البناء، نقوم بربط محرك مراقبة الأداء وتأسيس مجلد الكاش الخفي،
# حيث يتم البحث عن بيئة APPDATA على أنظمة ويندوز أو المجلد الرئيسي للمستخدم ~ على أنظمة لينكس ويونكس لإنشاء مجلد خفي
# باسم .moroia يحتوي على ملفات كاش التحديث update_cache.json وملف الإعدادات الأساسي config.json بشكل آمن ومنعزل تماماً.
# دالة load_language_preference تقوم بفتح ملف الإعدادات وقراءة كود اللغة المخزن بصيغة جيسون؛ وفي حال عدم وجود الملف أو حدوث
# خطأ في القراءة، يتم اعتماد اللغة الإنجليزية كخيار افتراضي لحماية استقرار التطبيق. دالة save_language_preference تقوم بتحديث
# متغير اللغة في الذاكرة الحية وفحص وجود المجلد الخفي، وإن لم يكن موجوداً تقوم بإنشائه فوراً عبر دالة os.makedirs ثم كتابة
# تفضيلات المستخدم الجديدة برمجياً. بعد ذلك، دالة setup_localization تبحث داخل المجلد الجغرافي للمشروع عن المسار الفرعي locale
# لمحاولة تحميل ملفات الترجمة المترجمة والجاهزة بامتدادات .mo؛ وفي حال عدم توفر تلك الملفات يتم تفعيل خط دفاع برمجي بديل وفوري.

class MoroiaEngine:
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.cache_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), '.moroia')
        self.cache_file = os.path.join(self.cache_dir, 'update_cache.json')
        self.config_file = os.path.join(self.cache_dir, 'config.json')
        self.current_lang = self.load_language_preference()
        self.setup_localization()

    def load_language_preference(self) -> str:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f).get('language', 'en')
            except: pass
        return 'en'

    def save_language_preference(self, lang: str):
        self.current_lang = lang
        if not os.path.exists(self.cache_dir):
            try: os.makedirs(self.cache_dir)
            except: pass
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'language': lang}, f)
        except: pass
        self.setup_localization()

    def setup_localization(self):
        localedir = os.path.join(os.path.dirname(__file__), 'locale')
        try:
            lang_trans = gettext.translation('moroia', localedir, languages=[self.current_lang])
            lang_trans.install()
            self._ = lang_trans.gettext
        except:
            self._ = lambda s: s

# ## 🚨 SECTION 4: ANTI-STALE VERSION ENFORCEMENT (منظومة فحص التحديثات الإجبارية الصارمة وحظر الإصدارات القديمة)
# ---
# في دالة check_for_updates نطبق استراتيجية صارمة لمنع استخدام أي إصدارات قديمة ومخترقة للأداة ولضمان تزامن المطورين.
# تقوم الدالة بجلب الوقت الحالي والمقارنة مع آخر طابع زمني تم تسجيله في ملف الكاش الخفي؛ فإذا تبين أن الفارق الزمني أقل
# من 10 دقائق كاملة، يتم تجاوز الفحص فوراً لتقليل استهلاك موارد الشبكة وتفادي حظر الـ IP من قِبل خوادم الهيئة الرسمية.
# أما إذا انقضت الـ 10 دقائق، تقوم الأداة بإطلاق طلب شبكي ذكي ومحدد بوقت استجابة صارم للغاية لا يتعدى 1.5 ثانية timeout=1.5
# متجهاً إلى واجهة الجيسون الرسمية لحزمة مورويا على الرابط الرسمي لبايثون. إذا نجح الاتصال وحصلنا على رمز الاستجابة 200،
# يتم استخراج رقم آخر إصدار مستقر مرفوع على الشبكة والمقارنة برقم المتغير العالمي المكتوب برمجياً داخل ملف الأداة VERSION.
# في حالة عدم التطابق، يُطلق المحرك بروتوكول الإغلاق الإجباري والتحديث الفوري، ويمسح الكونسول بالكامل ويعيد المؤشر ويطبع تحذيراً.

    def check_for_updates(self):
        now = datetime.now()
        should_check = False
        if not os.path.exists(self.cache_dir):
            try: os.makedirs(self.cache_dir)
            except: pass
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    last_str = data.get('last_check', '')
                    if last_str and now - datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S") > timedelta(minutes=10):
                        should_check = True
            except: should_check = True
        else: should_check = True

        if should_check:
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump({'last_check': now.strftime("%Y-%m-%d %H:%M:%S")}, f)
                res = requests.get("https://pypi.org/pypi/moroia/json", timeout=1.5)
                if res.status_code == 200 and res.json()["info"]["version"] != VERSION:
                    latest = res.json()["info"]["version"]
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"{Colors.CLEAR_SCREEN}{Colors.SHOW_CURSOR}")
                    print(f"{Colors.FAIL}{Colors.BOLD}🚨 UPDATE REQUIRED / تحديث مطلوب 🚨{Colors.ENDC}")
                    print(f"{Colors.WARNING}New Version available: v{latest} (Current: v{VERSION}){Colors.ENDC}\n")
                    print(f"{Colors.BOLD}👉 Run command to update / نفّذ الأمر للتحديث:{Colors.ENDC}")
                    print(f"{Colors.GREEN}{Colors.BOLD}   pip install --upgrade moroia --no-cache-dir{Colors.ENDC}\n")
                    sys.exit(0)
            except: pass

# ## 💻 SECTION 5: HARDWARE AGGREGATION & GPU DETECTOR (منظومة استخراج بيانات العتاد والعمليات والـ GPU منخفضة المستوى)
# ---
# تعتبر دالة get_hardware_status بمثابة micro-intelligence للعتاد. تبدأ بالتحقق من وجود مكتبة psutil فإن غابت ترجع خطأ.
# نقوم بسحب استهلاك المعالج الفوري بدون إحداث أي بطء في التدفق الحركي عبر تمرير معامل الأمان القياسي interval=None.
# بعد ذلك نأخذ لقطة سريعة للذاكرة العشوائية ومساحة القرص الصلب الرئيسي المتمثل في الجذر /. لحساب واكتشاف أكثر البرامج استهلاكاً
# للذاكرة (Heavy Apps)، نقوم بفتح حلقة تكرارية مرنة تمر على جميع العمليات النشطة في نظام التشغيل وتسحب منها اسم العملية،
# ونسبة استهلاك الذاكرة، ونسبة المعالج عبر دالة psutil.process_iter مع حماية الحلقة بالكامل ضد استثناءات حظر الوصول أو الموت المفاجئ.
# نقوم بفرز القائمة تنازلياً وفقاً لحجم استهلاك الذاكرة، ثم نلتقط أعلى عمليتين فقط تلتهمان موارد النظام، ونقصهما عند الطول الحجمي
# 12 حرفاً للحفاظ على ثبات الواجهة الرسومية الشبكية. في النهاية، ومن أجل جلب اسم كرت الشاشة الحقيقي بدقة متناهية على ويندوز،
# نقوم بتوظيف دالة سفلية تطلق أمر الاستعلام الخاص بالنظام عبر أداة الإدارة wmic مع وضع مهلة زمنية قاطعة قدرها ثانيتان فقط.

    @staticmethod
    def get_hardware_status():
        if not psutil: return {"error": "psutil missing"}
        cpu_usage = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        heavy_apps = []
        try:
            procs = []
            for p in psutil.process_iter(['name', 'memory_percent', 'cpu_percent']):
                try:
                    p_info = p.info
                    if p_info['name'] and not p_info['name'].startswith('['): procs.append(p_info)
                except: continue
            procs.sort(key=lambda x: x.get('memory_percent', 0) or 0, reverse=True)
            for p in procs[:2]:
                name = p.get('name', 'Unknown')
                mem = p.get('memory_percent', 0) or 0
                if mem > 0.1: heavy_apps.append(f"{name[:12]} ({mem:.1f}%)")
        except: pass
        
        gpu_name = "Unknown"
        try:
            if platform.system() == "Windows":
                cmd = "wmic path win32_VideoController get name"
                gpu_out = subprocess.check_output(cmd, shell=True, text=True, timeout=2).split('\n')
                if len(gpu_out) > 1 and gpu_out[1].strip(): gpu_name = gpu_out[1].strip()[:25]
        except: pass
        
        return {
            "cpu_usage_pct": cpu_usage,
            "ram_total_gb": round(ram.total / (1024**3), 1),
            "ram_usage_pct": ram.percent,
            "ram_used_gb": round((ram.total - ram.available) / (1024**3), 1),
            "disk_free_gb": round(disk.free / (1024**3), 1),
            "disk_total_gb": round(disk.total / (1024**3), 1),
            "gpu": gpu_name,
            "heavy_apps": heavy_apps if heavy_apps else ["None"]
        }

# ## 🛡️ SECTION 6: SPY HUNTER SECURITY AUDIT & NET-SCOUT (منظومة تتبع الاتصالات الخبيثة الحية وجلب عناوين الـ IP السريعة)
# ---
# تعتبر منظومة الـ spy_hunter_scan الذراع الأمني للأداة. تقوم الدالة بفحص جميع المقابس والاتصالات الشبكية المفتوحة حالياً
# في الخلفية باستخدام نظام البحث عالي الكفاءة psutil.net_connections مع تصفية نوع المقابس إلى inet (أي اتصالات الإنترنت فقط).
# تمر الدالة عبر جميع الاتصالات المفتوحة وتبحث بدقة عن الحالات المستقرة والنشطة التي تحمل الحالة السيادية ESTABLISHED والتي تمتلك
# عنوان آي بي خارجي حقيقي موجّه raddr؛ ومن ثم نقوم بتطبيق فلتر كاشف وصارم يستبعد فوراً عناوين الاسترجاع المحلي والآي بي الداخلي.
# أي اتصال ينجح في تخطي هذا الفلتر يتم تتبعه ومعرفة رقم المعرف البرمجي الخاص به pid؛ ومنه نسحب الاسم الصريح للبرنامج المسبب
# للاتصال ونقوم بوضعه فوراً في قائمة التهديدات المحتملة. أما دالة get_network_info فتقوم بحيلة برمجية فائقة السرعة لاستخراج
# الآي بي الداخلي للمستخدم دون الحاجة لربط حقيقي، حيث تفتح مقبس خفيف وتتصل وهمياً بـ DNS جوجل الشهير لتسجيل العنوان ثم إغلاقه.

    @staticmethod
    def spy_hunter_scan() -> List[Dict[str, Any]]:
        suspicious = []
        if not psutil: return suspicious
        try:
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    remote_ip = conn.raddr[0]
                    if remote_ip not in ['127.0.0.1', '::1', '0.0.0.0']:
                        pid = conn.pid
                        proc_name = "Unknown"
                        if pid:
                            try: proc_name = psutil.Process(pid).name()
                            except: continue
                        suspicious.append({"pid": pid, "process": proc_name[:12], "remote": remote_ip})
        except: pass
        return suspicious[:2]

    @staticmethod
    def get_network_info():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except: local_ip = "127.0.0.1"
        
        public_ip = "Unknown"
        try: public_ip = requests.get("https://api.ipify.org", timeout=1.5).text.strip()
        except: pass
        return {"local": local_ip, "public": public_ip}

# ## 🧹 SECTION 7: TURBO DISK PURGER & PIP CACHE REVIVER (منظومة تنظيف الذاكرة ومخلفات المطورين وحساب الأوتوبايلوت بالأحجام)
# ---
# هنا نكشف عن آليات الصيانة العميقة للأداة من خلال دوال التنظيف الحقيقية وحساب الأحجام بالبايت. دالة clear_temp_files تستهدف مسارات
# الملفات المؤقتة المتراكمة في بيئة نظام تشغيل ويندوز عبر البحث في متغير البيئة TEMP ومجلد النظام الرئيسي بشكل مباشر؛ تقوم الدالة
# بالدخول وفحص كل ملف، وإذا تم تفعيل الـ safe_mode يتم استبعاد الملفات النشطة لحماية البرامج الحالية من الانهيار، بينما يتم حساب الحجم
# الفعلي لكل ملف تالف ومسحه نهائياً عبر os.unlink. في نفس السياق، دالة clear_developer_cache تحل واحدة من أكبر مشاكل مطوري بايثون
# وهي تضخم كاش أداة التثبيت pip؛ حيث تحدد الدالة المسار الجغرافي الدقيق لكاش المطور سواء كان على ويندوز أو لينكس. تقوم الدالة
# بعمل مسح شجري متكامل وحساب الأحجام بالبايت وتجميعها بدقة؛ ثم تنسف المجلد بالكامل من جذوره باستخدام دالة القوة shutil.rmtree.

    @staticmethod
    def clear_temp_files(safe_mode: bool = True) -> int:
        if platform.system() != 'Windows': return 0
        temp_paths = [os.environ.get('TEMP', ''), os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp')]
        freed_bytes = 0
        for path in temp_paths:
            if not path or not os.path.exists(path): continue
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if safe_mode and time.time() - os.path.getmtime(file_path) < 3600: continue
                    if os.path.isfile(file_path):
                        freed_bytes += os.path.getsize(file_path)
                        os.unlink(file_path)
                except: continue
        return freed_bytes

    @staticmethod
    def clear_developer_cache() -> int:
        freed_bytes = 0
        path = os.path.expanduser(r"~\AppData\Local\pip\cache") if platform.system() == 'Windows' else os.path.expanduser("~/.cache/pip")
        if os.path.exists(path):
            try:
                for root, dirs, files in os.walk(path):
                    for f in files:
                        try: freed_bytes += os.path.getsize(os.path.join(root, f))
                        except: pass
                shutil.rmtree(path, ignore_errors=True)
            except: pass
        return freed_bytes

# ## 🎨 SECTION 8: MATHEMATICAL GRID DRAWING & ANTI-FLICKER DASHBOARD (نظام الرسم الهندسي والشبكة المقاومة للوميض والرمشة)
# ---
# تتحكم دالة make_bar رياضياً في طريقة رسم أشرطة استهلاك الموارد الأنيقة؛ فهي تأخذ النسبة المئوية الممررة وتقوم بحساب طردي لتحديد
# عدد المربعات المصمتة █ والمربعات الباهتة ░ بناءً على طول ثابت وصارم هو 20 حيزاً نصياً فقط لضمان عدم حدوث أي تمدد أو تشوه في الشبكة.
# بعد ذلك، دالة print_clean_dashboard تقوم ببناء لوحة التحكم الفائقة النقاء الشبكي؛ حيث ترسم الحدود الصارمة بدقة خطية باستخدام
# الرموز الهندسية المصمتة وتدمج في خلاياها العلوية وقت التشغيل الإجمالي، وتفتح جدولين متوازيين يعرضان استهلاك المعالج كنسبة وشريط
# ملون ديناميكياً (أخضر للاستهلاك الآمن، أصفر للمتوسط، وأحمر للخطر الفوري) وبجانبه استهلاك الذاكرة العشوائية الدقيق بالميجابايت.
# لضمان القضاء التام والمطلق على مشكلة رمشة الشاشة المزعجة (Flickering Effect)، لا نستخدم دالة مسح الشاشة العنيفة والبطيئة؛ بل نقوم
# ببث تتابع الهروب الذكي عالي السرعة \033[H في بداية حلقة التحديث داخل الدالة الرئيسية، والذي يجبر مؤشر ترمينال النظام على القفز الفوري.

def make_bar(pct: float, color: str) -> str:
    length = 20
    filled = int((pct / 100) * length)
    return f"{color}{'█' * filled}{Colors.DIM}{'░' * (length - filled)}{Colors.ENDC}"

def print_clean_dashboard(hw, network, spy, uptime_str, time_left, _):
    cpu_pct = hw.get('cpu_usage_pct', 0)
    ram_pct = hw.get('ram_usage_pct', 0)
    
    cpu_color = Colors.GREEN if cpu_pct < 50 else Colors.WARNING if cpu_pct < 85 else Colors.FAIL
    ram_color = Colors.GREEN if ram_pct < 60 else Colors.WARNING if ram_pct < 85 else Colors.FAIL
    
    print(f" {Colors.MAIN_THEME}┌──────────────────────────────────────────────────────────────┐{Colors.ENDC}")
    print(f" {Colors.MAIN_THEME}│{Colors.ENDC} {Colors.BOLD}📊 {_('DASHBOARD CONTROL CENTER')} {Colors.ENDC}          {_('Uptime')}: {Colors.GREEN}{uptime_str}{Colors.ENDC}  {Colors.MAIN_THEME}│{Colors.ENDC}")
    print(f" {Colors.MAIN_THEME}├──────────────────────────────┬───────────────────────────────┤{Colors.ENDC}")
    
    cpu_bar = make_bar(cpu_pct, cpu_color)
    ram_bar = make_bar(ram_pct, ram_color)
    print(f" {Colors.MAIN_THEME}│{Colors.ENDC} {Colors.BOLD}💻 CPU LOAD:{Colors.ENDC} {cpu_color}{cpu_pct:4.1f}%{Colors.ENDC}         {Colors.MAIN_THEME}│{Colors.ENDC} {Colors.BOLD}🧠 RAM USAGE:{Colors.ENDC} {ram_color}{ram_pct:4.1f}%{Colors.ENDC}        {Colors.MAIN_THEME}│{Colors.ENDC}")
    print(f" {Colors.MAIN_THEME}│{Colors.ENDC} {cpu_bar}  {Colors.MAIN_THEME}│{Colors.ENDC} {ram_bar}    {Colors.MAIN_THEME}│{Colors.ENDC}")
    print(f" {Colors.MAIN_THEME}│{Colors.ENDC} GPU: {hw['gpu']:<24} {Colors.MAIN_THEME}│{Colors.ENDC} RAM Status: {hw['ram_used_gb']}/{hw['ram_total_gb']} GB      {Colors.MAIN_THEME}│{Colors.ENDC}")
    
    print(f" {Colors.MAIN_THEME}├──────────────────────────────┴───────────────────────────────┤{Colors.ENDC}")
    
    apps_str = ", ".join(hw['heavy_apps'])
    print(f" {Colors.MAIN_THEME}│{Colors.ENDC} 💿 {_('Disk Storage')}: {hw['disk_free_gb']} GB free / {hw['disk_total_gb']} GB Total                  {Colors.MAIN_THEME}│{Colors.ENDC}")
    print(f" {Colors.MAIN_THEME}│{Colors.ENDC} 🔥 {_('Top Apps Open')}: {Colors.WARNING}{apps_str[:40]:<45}{Colors.ENDC} {Colors.MAIN_THEME}│{Colors.ENDC}")
    print(f" {Colors.MAIN_THEME}│{Colors.ENDC} 🌐 {_('Network Local/Public')}: {Colors.CYAN}{network['local']}{Colors.ENDC} / {Colors.CYAN}{network['public']}{Colors.ENDC}              {Colors.MAIN_THEME}│{Colors.ENDC}")
    
    spy_status = f"{Colors.GREEN}SECURE (0){Colors.ENDC}" if not spy else f"{Colors.FAIL}ALERT ({len(spy)}){Colors.ENDC}"
    print(f" {Colors.MAIN_THEME}│{Colors.ENDC} 🛡️  {_('Spy Hunter Network Audit')}: {spy_status:<46} {Colors.MAIN_THEME}│{Colors.ENDC}")
    if spy:
        for s in spy[:1]:
            print(f" {Colors.MAIN_THEME}│{Colors.ENDC}    ↳ [SUSPICIOUS CONNECTION] -> Process: {Colors.FAIL}{s['process']}{Colors.ENDC} Remote: {Colors.WARNING}{s['remote']}{Colors.ENDC} {Colors.MAIN_THEME}│{Colors.ENDC}")
            
    print(f" {Colors.MAIN_THEME}└──────────────────────────────────────────────────────────────┘{Colors.ENDC}")
    print(f"\n   {Colors.WARNING}💡 {_('Press Ctrl+C to open optimization & autopilot menu')}{Colors.ENDC}")

# ## 💎 SECTION 9: REVOLUTION BANNER & APPLICATION ENTRY POINT (شعار الثورة البرمجية ونقطة الانطلاق الحية واعتبارات التحكم)
# ---
# نقوم برسم الشعار النصي الفخم للأداة ليعبر عن روح القوة الجبارة للإصدار الرابع عبر دالة print_banner المصبوغة بالكامل بالثيم الموحد لمالك.
# نأتي الآن للدالة الحركية والقلب التنفيذي الشامل main. تبدأ فوراً بحقن أمر التصفية والمسح الأولي وإخفاء المؤشر تماماً لتجهيز الكونسول للبث الحي؛
# ثم تستدعي دالة فحص الآي بي لمرة واحدة فقط وتخزن مخرجاتها في الذاكرة لتجنب استعلامها المتكرر داخل الحلقة الذي يسبب تجمد الواجهة ثانية تلو الأخرى.
# تدخل الأداة في حلقة لا نهائية تحدّث البيانات كل ثانية وتتحكم في موضع طباعتها بدقة مطلقة عبر توجيه خيط المعالجة الرئيسي وإرسال قيم الترجمة الفعالة.
# عندما يقوم المستخدم بالضغط على الاختصار الحاسم Ctrl + C يتم اعتراض الاستثناء فوراً وبسلاسة تامة عبر بنية الـ KeyboardInterrupt؛
# حيث يفتح البرنامج خط حماية عالي الاستقرار يعيد إظهار مؤشر سطر الأوامر المخفي ويمسح الشاشة ليعرض قائمة الـ Autopilot التفاعلية المتقدمة،
# والتي تتيح للمستخدم إما إجراء تنظيف تيربو ذكي وفوري مع حساب المساحة المستردة الفعالة بالميجابايت بدقة متناهية، أو تبديل لغة الواجهة فوراً.

def print_banner():
    print(f"""
{Colors.CYAN}  ============================================================= {Colors.ENDC}
{Colors.BOLD}{Colors.MAIN_THEME}     __  __  ____  _____   ____  _____  _      /\  
     |  \/  |/ __ \|  __ \ / __ \|_    _|| |    /  \ 
     | \  / | |  | | |__) | |  | | | |  | |   /    \ 
     | |\/| | |  | |  _  /| |  | | | |  | |  /  /\  \ 
     | |  | | |__| | | \ \| |__| |_| |_ | |_/ ____  \ 
     |_|  |_|\____/|_|  \_\____/|_____||_/_/    \_\ {Colors.ENDC}
{Colors.BOLD}{Colors.CYAN}               💎 MOROIA REVOLUTION ENGINE v{VERSION} 💎          {Colors.ENDC}
{Colors.CYAN}  ============================================================= {Colors.ENDC}""")

def main():
    engine = MoroiaEngine()
    engine.check_for_updates()
    _ = engine._
    
    print(f"{Colors.CLEAR_SCREEN}{Colors.HIDE_CURSOR}", end="")
    network_data = engine.get_network_info()
    
    try:
        while True:
            hw = engine.get_hardware_status()
            spy_data = engine.spy_hunter_scan()
            uptime_str = engine.monitor.get_uptime_string()
            engine.monitor.update()
            
            print("\033[H", end="")
            print_banner()
            print_clean_dashboard(hw, network_data, spy_data, uptime_str, 0, _)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"{Colors.SHOW_CURSOR}{Colors.CLEAR_SCREEN}")
        print_banner()
        
        print(f"\n {Colors.BOLD}{Colors.CYAN}⚡ AUTOPILOT PERFORMANCE MENU{Colors.ENDC}")
        print(" ──────────────────────────────────────────────────────────────")
        print(f"  [1] {_('Run Full Smart Turbo Clean (Temp & Pip Caches)')}")
        print(f"  [2] {_('Toggle Interface Language (English / العربية)')}")
        print(f"  [3] {_('Exit Engine')}")
        
        try:
            choice = input(f"\n {Colors.BOLD}{_('Enter Action (1-3): ')}{Colors.ENDC}").strip()
            if choice == '1':
                print(f"\n {Colors.CYAN}⏳ Analyzing system and flushing dump caches...{Colors.ENDC}")
                b_temp = MoroiaEngine.clear_temp_files(safe_mode=False)
                b_pip = MoroiaEngine.clear_developer_cache()
                total_mb = round((b_temp + b_pip) / (1024**2), 2)
                print(f" {Colors.GREEN}✅ Turbo Clean Complete! {total_mb} MB of Storage/Disk Cache Revived.{Colors.ENDC}")
            elif choice == '2':
                nxt = 'ar' if engine.current_lang == 'en' else 'en'
                engine.save_language_preference(nxt)
                print(f" {Colors.GREEN}Language toggled to: {nxt}. Please reload Moroia.{Colors.ENDC}")
            elif choice == '3':
                sys.exit(0)
                
            print(f"\n {Colors.MAIN_THEME}{_('Press Enter to finish...')}{Colors.ENDC}")
            input()
        except: pass
    finally:
        print(f"{Colors.SHOW_CURSOR}{Colors.CLEAR_SCREEN}", end="")

if __name__ == '__main__':
    main()

# ## 🚀 SECTION 10: SECURE PIP DEPLOYMENT WORKFLOW (خريطة النشر والرفع والانتشار الرسمي الآمن على PyPI والـ PowerShell خطوة بخطوة)
# ---
# لكي تضمن نشر الأداة للعامة والمجتمع البرمجي المفتوح على PyPI بشكل احترافي خالٍ تماماً من الملفات الميتة أو تداخل مخلفات الإصدارات
# السابقة، يتعين عليك تنظيم مجلد المشروع بهندسة معيارية صارمة تحتوي على ملفات الإعداد الفعالة وهي setup.py و pyproject.toml مع ضبط
# نقطة الدخول الرئيسية لتربط كلمة أمر التشغيل moroia مباشرة باستدعاء الدالة التنفيذية main الموجودة بداخل الملف النقي للمشروع.
# نوفر لك هنا السطر السحري الخطي الموحد عالي السرعة والمخصص للتشغيل الفوري داخل بيئة الـ PowerShell أو الـ Terminal؛ حيث يقوم هذا السطر
# برمجياً بمسح مجلدات التوزيع القديمة dist ومجلد البناء build وملفات معلومات البيضة النشطة egg-info إجبارياً وبدون إطلاق أي استثناءات،
# ثم يستدعي فوراً وحدة التجميع الرسمية لبايثون لإنشاء حزم الـ Wheel والـ Source Tarball بشكل مضغوط ومثالي للإصدار الراديكالي الجديد.
# Command: Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue; python -m build; python -m twine upload --username __token__ dist/*

# ## 🧪 SECTION 11: FULL DECOUPLED TESTING PROTOCOL (بروتوكول الفحص النظيف والتجربة الحية المعزولة وإلغاء الكاش المحلي)
# ---
# لضمان فحص الأداة بعد النشر والتأكد من تفعيل جميع آليات الحماية والتحديث الإجباري والواجهة الرسومية الثابتة والجديدة، يجب تفادي فخاخ
# كاش نظام التشغيل المحلي الذي يدمج حزم الـ wheels القديمة من الذاكرة المحلية للجهاز. يتم تفعيل البروتوكول الاختباري الصارم عبر ثلاثة
# أوامر متتالية تضمن العزل الكامل؛ حيث يقوم الأمر الأول بحذف أي بقايا أو مخلفات برمجية قديمة للأداة من بيئة بايثون بشكل صامت، تتبعه دالة
# التصفية الشاملة لكاش أداة التثبيت القياسية لنسف أي ملفات مخزنة مسبقاً في الهارد ديسك الخاص بنظام التشغيل، ليأتي الأمر الثالث الحاسم
# بتحميل وتثبيت حزمة مورويا بإصدارها الثوري الجديد 4.0.0 مباشرة من الخوادم السحابية الرسمية لـ PyPI مع إجبار أداة التثبيت على تجاهل الكاش.
# Command 1: pip uninstall moroia -y
# Command 2: pip cache purge
# Command 3: pip install moroia==4.0.0 --no-cache-dir
# Command 4: moroia
# ======================================================================================================================
#                                         🔥 END OF BLUEPRINT | ARCHITECTURE VERIFIED 🔥
# ======================================================================================================================
