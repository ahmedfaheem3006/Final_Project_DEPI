# ================================
# تثبيت المكتبات
# ================================
# !pip install gradio openai --quiet
import gradio as gr
import json
import time
import re
import os
from datetime import datetime
import requests
import tempfile
from PIL import Image

# التحقق من توفر مكتبة OpenAI
try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    print("OpenAI library not available. Using mock image generation.")
    OpenAI = None
    openai_available = False

# ================================
# تهيئة OpenAI API
# ================================
# تحميل متغيرات البيئة من ملف .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")

# يمكن للمستخدم تعيين مفتاح API إما من متغير البيئة أو من هنا مباشرة
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Set your OpenAI API key here

if openai_available and OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
elif openai_available and not OPENAI_API_KEY:
    print("Warning: OpenAI API key not set. Using mock image generation instead.")
    print("  To use real image generation, add your API key.")
    client = None
else:
    print("Warning: OpenAI library not available. Using mock image generation.")
    client = None

# ================================
# بيانات افتراضية في حالة عدم وجود الملفات
# ================================
DEFAULT_FURNITURE = {
    "كنبة": {
        "models": [
            {"name": "كنبة مودرن 3 أفراد", "available_colors": ["أحمر", "أزرق", "رمادي", "أسود"], "materials": ["قُماش", "جِلْد"]},
            {"name": "كنبة كلاسيك منجدة", "available_colors": ["بني", "ذهبي", "أخضر", "أبيض"], "materials": ["قُماش", "جِلْد"]}
        ]
    },
    "كرسي": {
        "models": [
            {"name": "كرسي مكتب دوار", "available_colors": ["أسود", "رمادي", "أزرق"], "materials": ["بلاستيك", "معدن"]},
            {"name": "كرسي سفرة خشب", "available_colors": ["بني", "أبيض", "أصفر"], "materials": ["خشب"]}
        ]
    },
    "ترابيزة": {
        "models": [
            {"name": "ترابيزة سفرة خشب", "available_colors": ["بني", "أبيض"], "materials": ["خشب"]},
            {"name": "ترابيزة قهوة مودرن", "available_colors": ["أسود", "أبيض", "ذهبي"], "materials": ["زجاج", "معدن"]}
        ]
    }
}

DEFAULT_COLOURS = {
    "أحمر": "أحمر",
    "أزرق": "أزرق", 
    "أخضر": "أخضر",
    "أصفر": "أصفر",
    "أسود": "أسود",
    "أبيض": "أبيض",
    "رمادي": "رمادي",
    "بني": "بني",
    "ذهبي": "ذهبي",
    "فضي": "فضي"
}

DEFAULT_MATERIALS = {
    "خشب": "خشب",
    "معدن": "معدن", 
    "زجاج": "زجاج",
    "قُماش": "قُماش",
    "جِلْد": "جِلْد",
    "بلاستيك": "بلاستيك"
}

# ================================
# قراءة البيانات من الملفات مع البيانات الافتراضية
# ================================
def load_data():
    """تحميل البيانات من الملفات مع البيانات الافتراضية"""
    global commands, colours, furniture, materials
    
    # تحميل Furniture.txt
    try:
        # محاولة تحميل من المجلد المحلي أولاً
        local_path = os.path.join(os.path.dirname(__file__), "Furniture.txt")
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
        else:
            # إذا لم يكن موجودًا محليًا، استخدم المسار الأصلي
            with open("/content/Furniture.txt", "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
        # التحقق من أن البيانات محملة بشكل صحيح
        if isinstance(loaded_data, dict) and len(loaded_data) > 0:
            furniture = loaded_data
            print("Loaded Furniture.txt successfully")
        else:
            raise ValueError("File is empty or invalid")
    except Exception as e:
        print(f"Error loading Furniture.txt: {e}")
        print("Using default furniture data")
        furniture = DEFAULT_FURNITURE

    # تحميل Colours.txt
    try:
        # محاولة تحميل من المجلد المحلي أولاً
        local_path = os.path.join(os.path.dirname(__file__), "Colours.txt")
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
        else:
            # إذا لم يكن موجودًا محليًا، استخدم المسار الأصلي
            with open("/content/Colours.txt", "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
        if isinstance(loaded_data, dict) and len(loaded_data) > 0:
            colours = loaded_data
            print("Loaded Colours.txt successfully")
        else:
            raise ValueError("File is empty or invalid")
    except Exception as e:
        print(f"Error loading Colours.txt: {e}")
        print("Using default color data")
        colours = DEFAULT_COLOURS

    # تحميل matrials.txt
    try:
        # محاولة تحميل من المجلد المحلي أولاً
        local_path = os.path.join(os.path.dirname(__file__), "matrials.txt")
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
        else:
            # إذا لم يكن موجودًا محليًا، استخدم المسار الأصلي
            with open("/content/matrials.txt", "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
        if isinstance(loaded_data, dict) and len(loaded_data) > 0:
            materials = loaded_data
            print("Loaded matrials.txt successfully")
        else:
                raise ValueError("File is empty or invalid")
    except Exception as e:
        print(f"Error loading matrials.txt: {e}")
        print("Using default material data")
        materials = DEFAULT_MATERIALS

    # تحميل Commands.txt (اختياري)
    try:
        # محاولة تحميل من المجلد المحلي أولاً
        local_path = os.path.join(os.path.dirname(__file__), "Commands.txt")
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                commands = json.load(f)
        else:
            # إذا لم يكن موجودًا محليًا، استخدم المسار الأصلي
            with open("/content/Commands.txt", "r", encoding="utf-8") as f:
                commands = json.load(f)
        print("Loaded Commands.txt successfully")
    except Exception as e:
        print(f"Error loading Commands.txt: {e}")
        commands = {}

    print(f"Loaded data: {len(furniture)} furniture, {len(colours)} colors, {len(materials)} materials")

# تحميل البيانات أول مرة
load_data()

# ================================
# نظام الذاكرة
# ================================
class MemorySystem:
    def __init__(self):
        self.conversation_history = []
        self.added_items = []
        self.removed_items = []
        self.user_preferences = {}
        
    def add_to_history(self, role, content):
        """إضافة رسالة لتاريخ المحادثة"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # حفظ آخر 50 رسالة فقط
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def add_furniture(self, item, color=None, material=None):
        """إضافة قطعة أثاث للذاكرة"""
        furniture_item = {
            "item": item,
            "color": color,
            "material": material,
            "timestamp": datetime.now().isoformat()
        }
        self.added_items.append(furniture_item)
        print(f"✅ تم إضافة {item} للذاكرة")
    
    def remove_furniture(self, item):
        """إزالة قطعة أثاث من الذاكرة"""
        self.removed_items.append({
            "item": item,
            "timestamp": datetime.now().isoformat()
        })
        # إزالة من القائمة المضافة
        self.added_items = [f for f in self.added_items if f["item"] != item]
        print(f"✅ تم حذف {item} من الذاكرة")
    
    def get_added_items(self):
        """الحصول على القطع المضافة"""
        return self.added_items.copy()
    
    def get_conversation_context(self, last_n=5):
        """الحصول على سياق المحادثة الأخير"""
        return self.conversation_history[-last_n:]

# إنشاء نظام الذاكرة
memory_system = MemorySystem()

# ================================
# دوال توليد الصور
# ================================
def generate_image_from_prompt(prompt):
    """توليد صورة من النص المدخل باستخدام OpenAI DALL-E أو إنشاء صورة وهمية"""
    # تحقق أولاً مما إذا كان العميل متاحًا
    if client is None:
        print("Skipped API call because OpenAI key is not set - using mock function")
        # إنشاء صورة وهمية مباشرة
        try:
            # إنشاء صورة بسيطة باستخدام PIL
            from PIL import Image, ImageDraw
            import random

            # إنشاء صورة فارغة
            img = Image.new('RGB', (512, 512), color=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
            d = ImageDraw.Draw(img)

            # رسم بعض الأشكال بسيطة
            d.rectangle([100, 100, 412, 412], outline=(255, 255, 255), width=3)
            d.text((200, 250), "Generated Image", fill=(255, 255, 255))
            d.text((180, 280), f"(prompt: {prompt[:20]}...)", fill=(200, 200, 200))

            # حفظ الصورة المؤقتة
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                img.save(tmp_file.name, 'PNG')
                return tmp_file.name
        except Exception as fallback_error:
            print(f"Failed to create mock image: {fallback_error}")
            return None

    try:
        # تحسين م_PROMPT لتحسين جودة الصورة
        enhanced_prompt = f"realistic, high quality, detailed furniture: {prompt}, professional photography, interior design, 4k, photorealistic"

        response = client.images.generate(
            model="dall-e-2",
            prompt=enhanced_prompt,
            n=1,
            size="512x512"
        )

        image_url = response.data[0].url

        # تنزيل الصورة وحفظها مؤقتًا
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        # إنشاء ملف مؤقت لحفظ الصورة
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(image_response.content)
            return tmp_file.name

    except Exception as e:
        print(f"Error in image generation: {e}")
        print("Using mock image instead")
        # إنشاء صورة وهمية في حال فشل API
        try:
            # إنشاء صورة بسيطة باستخدام PIL
            from PIL import Image, ImageDraw
            import random

            # إنشاء صورة فارغة
            img = Image.new('RGB', (512, 512), color=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
            d = ImageDraw.Draw(img)

            # رسم بعض الأشكال بسيطة
            d.rectangle([100, 100, 412, 412], outline=(255, 255, 255), width=3)
            d.text((200, 250), "Generated Image", fill=(255, 255, 255))
            d.text((180, 280), f"(prompt: {prompt[:20]}...)", fill=(200, 200, 200))

            # حفظ الصورة المؤقتة
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                img.save(tmp_file.name, 'PNG')
                return tmp_file.name
        except Exception as fallback_error:
            print(f"Failed to create mock image too: {fallback_error}")
            return None

# ================================
# حالة الجلسة
# ================================
session_state = {
    "pending_action": None, 
    "pending_item": None,
    "pending_color": None,
    "pending_material": None,
    "current_context": None
}

# ================================
# دوال مساعدة محسنة
# ================================
def normalize_text(text):
    """تطبيع النص لإزالة التشكيل والتفاوتات في الكتابة"""
    if not text:
        return ""
        
    replacements = {
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ة': 'ه', 'ّ': '', 'َ': '', 'ُ': '', 'ِ': '',
        'ضيف': 'اضف', 'ضيفي': 'اضف', 'ضيفلي': 'اضف', 'نضيف': 'اضف',
        'الوان': 'الوان', 'الالوان': 'الوان', 
        'خامات': 'مواد', 'الخامات': 'مواد', 'المواد': 'مواد',
        'اثاث': 'اثاث', 'الاثاث': 'اثاث', 'الأثاث': 'اثاث',
        'موديلات': 'موديلات', 'الموديلات': 'موديلات',
        'عاوز': 'عايز', 'عايزة': 'عايز', 'عايزين': 'عايز',
        'ابغى': 'عايز', 'ابغي': 'عايز', 'اريد': 'عايز', 'نبي': 'عايز',
        'احذف': 'امسح', 'احذفي': 'امسح', 'شيل': 'امسح', 'شيلي': 'امسح', 'ازيل': 'امسح'
    }
    text = text.lower().strip()
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def detect_furniture(text):
    """اكتشاف نوع الأثاث من النص مع تحسين الدقة"""
    if not text:
        return None
        
    normalized_text = normalize_text(text)
    
    # إصلاح الخطأ: التحقق من أن furniture هو قاموس وليس نص
    if not isinstance(furniture, dict):
        print("❌ خطأ: furniture ليس قاموساً")
        return None
    
    # البحث المباشر في الأثاث
    for item in furniture.keys():
        if isinstance(item, str) and item in normalized_text:
            return item
    
    # البحث بالمرادفات
    furniture_synonyms = {
        'كنبه': 'كنبة', 'كنب': 'كنبة', 'أريكة': 'كنبة', 'سوفا': 'كنبة', 'أريكه': 'كنبة', 'كنبيه': 'كنبة',
        'كراسي': 'كرسي', 'مقعد': 'كرسي', 'مقاعد': 'كرسي', 'كورسي': 'كرسي', 'كرسى': 'كرسي',
        'منضده': 'ترابيزة', 'طاوله': 'ترابيزة', 'طاولة': 'ترابيزة', 'تافله': 'ترابيزة',
        'منضدة': 'ترابيزة', 'تابوره': 'ترابيزة', 'ترابيزه': 'ترابيزة', 'تربيزه': 'ترابيزة'
    }
    
    for synonym, actual in furniture_synonyms.items():
        if synonym in normalized_text:
            return actual
    
    return None

def detect_color(text):
    """اكتشاف اللون من النص"""
    if not text:
        return None
        
    normalized_text = normalize_text(text)
    
    # إصلاح الخطأ: التحقق من أن colours هو قاموس
    if not isinstance(colours, dict):
        print("❌ خطأ: colours ليس قاموساً")
        return None
    
    for color_key, color_value in colours.items():
        # البحث عن اللون مباشرة
        if isinstance(color_key, str) and color_key in normalized_text:
            return color_key
        
        # البحث في قيم الألوان
        if isinstance(color_value, str) and color_value in normalized_text:
            return color_key
    
    # البحث بالمرادفات
    color_synonyms = {
        'احمر': 'أحمر', 'حمرا': 'أحمر', 'حمراء': 'أحمر', 'احمرا': 'أحمر',
        'ازرق': 'أزرق', 'زرقا': 'أزرق', 'زرقاء': 'أزرق', 'ازرقا': 'أزرق',
        'اخضر': 'أخضر', 'خضرا': 'أخضر', 'خضراء': 'أخضر', 'اخضرا': 'أخضر',
        'اصفر': 'أصفر', 'صفرا': 'أصفر', 'صفراء': 'أصفر', 'اصفرا': 'أصفر',
        'اسود': 'أسود', 'سودا': 'أسود', 'سوداء': 'أسود', 'اسودا': 'أسود',
        'ابيض': 'أبيض', 'بيضا': 'أبيض', 'بيضاء': 'أبيض', 'ابيضا': 'أبيض',
        'رمادي': 'رمادي', 'رماديه': 'رمادي', 'رمادى': 'رمادي',
        'بني': 'بني', 'بنيه': 'بني', 'بنى': 'بني',
        'ذهبي': 'ذهبي', 'دهبي': 'ذهبي', 'ذهبى': 'ذهبي',
        'فضي': 'فضي', 'فضيه': 'فضي', 'فضى': 'فضي'
    }
    
    for synonym, actual in color_synonyms.items():
        if synonym in normalized_text:
            return actual
    
    return None

def detect_material(text):
    """اكتشاف المادة من النص"""
    if not text:
        return None
        
    normalized_text = normalize_text(text)
    
    # إصلاح الخطأ: التحقق من أن materials هو قاموس
    if not isinstance(materials, dict):
        print("❌ خطأ: materials ليس قاموساً")
        return None
    
    for material_key, material_value in materials.items():
        if isinstance(material_key, str) and material_key in normalized_text:
            return material_key
        if isinstance(material_value, str) and material_value in normalized_text:
            return material_key
    
    return None

def detect_intent(user_input):
    """تحليل النية من النص المدخل"""
    if not user_input:
        return "unknown"

    text = normalize_text(user_input)

    # أنماط للتعرف على النوايا
    add_patterns = [r'اضف', r'عايز اضف', r'ابغى اضف', r'اريد اضف', r'حاب اضف', r'نضيف']
    remove_patterns = [r'امسح', r'احذف', r'شيل', r'حذف', r'مسح', r'ازالة', r'الغاء']
    color_patterns = [r'الوان', r'الالوان', r'لون', r'اللون', r'ألوان']
    material_patterns = [r'مواد', r'المواد', r'خامات', r'الخامات', r'مادة', r'خامة']
    furniture_patterns = [r'اثاث', r'الاثاث', r'موديلات', r'الموديلات', r'قطع']
    change_patterns = [r'غير', r'تغيير', r'بدل', r'تعديل', r'عدل', r'تغير']
    help_patterns = [r'مساعدة', r'مساعده', r'help', r'ادعم', r'دعم', r'شرح']
    view_patterns = [r'عرض', r'شوف', r'ارني', r'ابي اشوف', r'عايز اشوف']
    memory_patterns = [r'ضيفنا', r'ضفت', r'مسحنا', r'حذفنا', r'اللى ضفت', r'اللى مسحنا']
    image_patterns = [r'صور', r'اريني', r'اعمل', r'صورة', r'/generated', r'image']  # نمط توليد الصور

    if any(re.search(pattern, text) for pattern in add_patterns):
        return "add_item"
    elif any(re.search(pattern, text) for pattern in remove_patterns):
        return "remove_item"
    elif any(re.search(pattern, text) for pattern in color_patterns):
        return "show_colors"
    elif any(re.search(pattern, text) for pattern in material_patterns):
        return "show_materials"
    elif any(re.search(pattern, text) for pattern in furniture_patterns):
        return "show_furniture"
    elif any(re.search(pattern, text) for pattern in change_patterns):
        return "change_item"
    elif any(re.search(pattern, text) for pattern in help_patterns):
        return "help"
    elif any(re.search(pattern, text) for pattern in view_patterns):
        return "view_items"
    elif any(re.search(pattern, text) for pattern in memory_patterns):
        return "view_memory"
    elif any(re.search(pattern, text) for pattern in image_patterns):
        return "generate_image"
    else:
        return "unknown"

def get_available_colors(item):
    """الحصول على الألوان المتاحة لقطعة أثاث"""
    if item not in furniture:
        return set()
    
    available_colors = set()
    for model in furniture[item].get("models", []):
        available_colors.update(model.get("available_colors", []))
    return available_colors

def get_available_materials(item):
    """الحصول على المواد المتاحة لقطعة أثاث"""
    if item not in furniture:
        return set()
    
    available_materials = set()
    for model in furniture[item].get("models", []):
        available_materials.update(model.get("materials", []))
    return available_materials

# ================================
# دالة الرد المحسنة مع الذاكرة
# ================================
def chatbot_response(user_input):
    global session_state
    
    if not user_input or not user_input.strip():
        return "🤔 لم أتلقى أي رسالة. هل يمكنك إعادة الكتابة؟"
    
    text = user_input.strip()
    
    # إضافة للمحادثة في الذاكرة
    memory_system.add_to_history("user", text)
    
    # تطبيع النص
    normalized_text = normalize_text(text)
    
    # اكتشاف العناصر
    try:
        item = detect_furniture(text)
        color = detect_color(text)
        material = detect_material(text)
        intent = detect_intent(text)
        
        print(f"🔍 التحليل: عنصر={item}, لون={color}, مادة={material}, نية={intent}")
        print(f"💾 حالة الجلسة: {session_state}")
    except Exception as e:
        print(f"❌ خطأ في الاكتشاف: {e}")
        response = "🤔 حدث خطأ في معالجة طلبك. حاول مرة أخرى."
        memory_system.add_to_history("assistant", response)
        return response
    
    # --------- حالة المساعدة ----------
    if intent == "help" or normalized_text in ["مساعدة", "مساعده", "help", "ادعم", "دعم", "شرح"]:
        response = "🛟 كيف أساعدك؟\n\n" \
                  "• إضافة أثاث: 'أضف كنبة' أو 'عايز أضيف كرسي'\n" \
                  "• حذف أثاث: 'امسح الكنبة' أو 'احذف الكرسي'\n" \
                  "• عرض الألوان: 'الألوان المتاحة للكنبة'\n" \
                  "• عرض المواد: 'الخامات المتاحة للكرسي'\n" \
                  "• رؤية كل الأثاث: 'عرض الأثاث' أو 'الموديلات'\n" \
                  "• رؤية اللى ضفتو: 'عرض اللى ضفت' أو 'شوف اللى مسحنا'\n" \
                  "• تغيير مواصفات: 'غير لون الكنبة'"
        memory_system.add_to_history("assistant", response)
        return response
    
    # --------- حالة عرض الذاكرة ----------
    if intent == "view_memory" or normalized_text in ["ضيفنا", "ضفت", "مسحنا", "اللى ضفت", "اللى مسحنا"]:
        added_items = memory_system.get_added_items()
        if added_items:
            items_list = []
            for i, item_data in enumerate(added_items, 1):
                item_desc = f"{i}. {item_data['item']}"
                if item_data['color']:
                    item_desc += f" - اللون: {item_data['color']}"
                if item_data['material']:
                    item_desc += f" - المادة: {item_data['material']}"
                items_list.append(item_desc)
            
            response = "🪑 القطع اللى ضفتها:\n" + "\n".join(items_list)
        else:
            response = "🪑 مفيش قطع أثاث مضيفة حالياً."
        memory_system.add_to_history("assistant", response)
        return response
    
    # --------- حالة إضافة عنصر ----------
    if intent == "add_item" or (item and not session_state["pending_action"] and any(word in normalized_text for word in ['اضف', 'عايز', 'ابغى', 'اريد'])):
        if item:
            # إذا تم تحديد العنصر، نطلب اللون
            session_state["pending_action"] = "awaiting_color"
            session_state["pending_item"] = item
            available_colors = get_available_colors(item)
            
            if available_colors:
                response = f"🪑 ممتاز! عايز تضيف {item} بإيه لون؟\n🎨 الألوان المتاحة: {', '.join(available_colors)}"
            else:
                response = f"🪑 تم اختيار {item}، لكن لا توجد ألوان محددة له."
        else:
            response = "🪑 عايز تضيف إيه؟ (مثل: كنبة، كرسي، ترابيزة)"
        memory_system.add_to_history("assistant", response)
        return response
    
    # --------- حالة حذف عنصر ----------
    if intent == "remove_item":
        if item:
            # البحث في الذاكرة عن العنصر لحذفه
            added_items = memory_system.get_added_items()
            item_found = any(f["item"] == item for f in added_items)
            
            if item_found:
                memory_system.remove_furniture(item)
                response = f"✅ تم مسح {item} من القائمة."
            else:
                response = f"❌ مفيش {item} في القائمة علشان امسحو."
        else:
            response = "🪑 عايز تمسح إيه؟ (مثل: امسح الكنبة أو احذف الكرسي)"
        memory_system.add_to_history("assistant", response)
        return response
    
    # --------- حالة انتظار اللون ----------
    if session_state["pending_action"] == "awaiting_color":
        if color:
            item = session_state["pending_item"]
            available_colors = get_available_colors(item)
            
            if color in available_colors:
                # إضافة العنصر للذاكرة
                memory_system.add_furniture(item, color, material)
                session_state.update({
                    "pending_action": None, 
                    "pending_item": None,
                    "pending_color": color
                })
                response = f"✅ تمت الإضافة بنجاح!\n🪑 {item} باللون {color} تمت إضافته."
            else:
                response = f"❌ اللون {color} غير متاح لـ {item}.\n🎨 الألوان المتاحة: {', '.join(available_colors)}"
        else:
            item = session_state["pending_item"]
            available_colors = get_available_colors(item)
            response = f"🪑 ما زلت أنتظر اختيار اللون لـ {item}.\n🎨 الألوان المتاحة: {', '.join(available_colors)}"
        memory_system.add_to_history("assistant", response)
        return response
    
    # --------- حالة عرض الألوان ----------
    if intent == "show_colors" or normalized_text in ["الوان", "الالوان", "اللون", "ألوان"]:
        if item:
            available_colors = get_available_colors(item)
            if available_colors:
                response = f"🎨 الألوان المتاحة لـ {item}:\n{', '.join(available_colors)}"
            else:
                response = f"❌ لا توجد ألوان محددة لـ {item}."
        elif session_state["pending_item"]:
            item = session_state["pending_item"]
            available_colors = get_available_colors(item)
            response = f"🎨 الألوان المتاحة لـ {item}:\n{', '.join(available_colors)}"
        else:
            response = "🎨 يرجى تحديد نوع الأثاث لمعرفة الألوان المتاحة.\nمثال: 'الألوان للكنبة' أو 'ألوان الكرسي'"
        memory_system.add_to_history("assistant", response)
        return response
    
    # --------- حالة عرض المواد ----------
    if intent == "show_materials" or normalized_text in ["مواد", "المواد", "خامات", "الخامات", "مادة", "خامة"]:
        if item:
            available_materials = get_available_materials(item)
            if available_materials:
                response = f"🛠️ المواد المتاحة لـ {item}:\n{', '.join(available_materials)}"
            else:
                response = f"❌ لا توجد مواد محددة لـ {item}."
        elif session_state["pending_item"]:
            item = session_state["pending_item"]
            available_materials = get_available_materials(item)
            response = f"🛠️ المواد المتاحة لـ {item}:\n{', '.join(available_materials)}"
        else:
            response = "🛠️ يرجى تحديد نوع الأثاث لمعرفة المواد المتاحة.\nمثال: 'المواد للكرسي' أو 'خامات الكنبة'"
        memory_system.add_to_history("assistant", response)
        return response
    
    # --------- حالة عرض الأثاث ----------
    if intent == "show_furniture" or normalized_text in ["الاثاث", "الأثاث", "موديلات", "الموديلات", "عرض الاثاث", "عرض الأثاث", "قطع"]:
        if not furniture:
            response = "❌ لا توجد بيانات للأثاث متاحة حالياً."
        else:
            items_list = []
            for itm, info in furniture.items():
                models = [m['name'] for m in info.get("models", [])]
                items_list.append(f"• {itm} - الموديلات: {', '.join(models)}")
            response = "🪑 الأثاث المتاح:\n" + "\n".join(items_list)
        memory_system.add_to_history("assistant", response)
        return response
    
    # --------- حالة عرض القطع المضافة ----------
    if intent == "view_items":
        added_items = memory_system.get_added_items()
        if added_items:
            items_list = []
            for i, item_data in enumerate(added_items, 1):
                item_desc = f"{i}. {item_data['item']}"
                if item_data['color']:
                    item_desc += f" - اللون: {item_data['color']}"
                if item_data['material']:
                    item_desc += f" - المادة: {item_data['material']}"
                items_list.append(item_desc)
            
            response = "🪑 القطع اللى عندك:\n" + "\n".join(items_list)
        else:
            response = "🪑 مفيش قطع أثاث مضيفة حالياً. تقدر تضيف قطع باستخدام 'أضف كنبة' أو 'عايز أضيف كرسي'"
        memory_system.add_to_history("assistant", response)
        return response
    
    # --------- حالة توليد الصور ----------
    if intent == "generate_image":
        # Extract the image description from the user input
        image_description = text
        if item:
            image_description = f"{item}"
            if color:
                image_description += f" {color}"
            if material:
                image_description += f" {material}"
            image_description += " furniture piece"
        # If user wants to generate a specific image, extract the description
        elif any(word in normalized_text for word in ['صورة', 'اريني', 'اعمل', 'صور']):
            # Extract the main content after image-related words
            match = re.search(r'(صورة|اريني|اعمل|صور)\s+(.+)', text, re.IGNORECASE)
            if match:
                image_description = match.group(2).strip()
            else:
                image_description = text.replace('صورة', '').replace('اريني', '').replace('اعمل', '').replace('صور', '').strip()

        response = "Generating image..."
        memory_system.add_to_history("assistant", response)

        # Generate the image
        image_path = generate_image_from_prompt(image_description)
        if image_path:
            response = f"Successfully generated an image for '{image_description}'!"
            memory_system.add_to_history("assistant", response)
            return [response, image_path]  # Return both text and image path
        else:
            response = "Failed to generate the image. Please try a different description."
            memory_system.add_to_history("assistant", response)
            return response

    # --------- حالة تغيير العنصر ----------
    if intent == "change_item":
        if item and color:
            available_colors = get_available_colors(item)
            if color in available_colors:
                # تحديث الذاكرة
                added_items = memory_system.get_added_items()
                for furniture_item in added_items:
                    if furniture_item["item"] == item:
                        furniture_item["color"] = color
                        if material:
                            furniture_item["material"] = material
                response = f"✅ تم تغيير {item} إلى اللون {color}."
            else:
                response = f"❌ اللون {color} غير متاح لـ {item}.\n🎨 الألوان المتاحة: {', '.join(available_colors)}"
        elif item:
            response = f"🪑 عايز تغير إيه في {item}؟ (اللون، المادة، إلخ)"
        else:
            response = "🪑 عايز تغير إيه؟ حدد العنصر أولاً."
        memory_system.add_to_history("assistant", response)
        return response
    
    # --------- رد افتراضي مع مساعدة ----------
    if item:
        # إذا تم التعرف على العنصر ولكن لم يتم فهم النية
        response = f"🪑 تم التعرف على {item}. ماذا تريد أن تفعل؟\n" \
                  f"• 'أضف {item}' - لإضافته\n" \
                  f"• 'الألوان لـ {item}' - لرؤية الألوان\n" \
                  f"• 'المواد لـ {item}' - لرؤية الخامات\n" \
                  f"• 'امسح {item}' - لحذفه"
        memory_system.add_to_history("assistant", response)
        return response
    
    # --------- إذا لم يفهم أي شيء ----------
    response = "🤔 لم أفهم طلبك. جرب:\n" \
              "• 'أضف كنبة' - لإضافة أثاث\n" \
              "• 'امسح كرسي' - لحذف أثاث\n" \
              "• 'الألوان' - لرؤية الألوان\n" \
              "• 'المواد' - لرؤية الخامات\n" \
              "• 'عرض اللى ضفت' - لرؤية القطع المضافة\n" \
              "• 'المساعدة' - للحصول على دليل الاستخدام"
    memory_system.add_to_history("assistant", response)
    return response

# ================================
# تأثير الكتابة البطيئة
# ================================
def delayed_typing(text):
    if not text:
        yield ""
        return
        
    displayed = ""
    for char in text:
        displayed += char
        yield displayed
        time.sleep(0.01)

# ================================
# دوال مساعدة للواجهة
# ================================
def handle_quick_action(action, chat_history):
    """معالجة الإجراءات السريعة"""
    try:
        response = chatbot_response(action)
        if not chat_history:
            chat_history = []
        chat_history.append({"role": "user", "content": f"[إجراء سريع] {action}"})

        # Check if response is a list (text + image path)
        if isinstance(response, list) and len(response) == 2:
            text_response, image_path = response
            chat_history.append({"role": "assistant", "content": text_response})
            chat_history.append({"role": "assistant", "content": image_path})
        else:
            chat_history.append({"role": "assistant", "content": response})

        return chat_history
    except Exception as e:
        error_msg = f"❌ حدث خطأ في الإجراء السريع: {str(e)}"
        if not chat_history:
            chat_history = []
        chat_history.append({"role": "assistant", "content": error_msg})
        return chat_history

def clear_chat():
    """مسح المحادثة وإعادة تعيين الحالة"""
    global session_state, memory_system
    session_state = {
        "pending_action": None, 
        "pending_item": None,
        "pending_color": None,
        "pending_material": None,
        "current_context": None
    }
    # إعادة تحميل البيانات من الملفات
    load_data()
    # إعادة تعيين الذاكرة
    memory_system = MemorySystem()
    return []

# ================================
# واجهة Gradio محسنة
# ================================
def chat_fn(message, chat_history):
    """دالة المحادثة الرئيسية"""
    try:
        response = chatbot_response(message)
        if not chat_history:
            chat_history = []

        chat_history.append({"role": "user", "content": message})

        # Check if response is a list (text + image path)
        if isinstance(response, list) and len(response) == 2:
            text_response, image_path = response

            # Add the final message with both text and image immediately
            chat_history.append({"role": "assistant", "content": text_response})
            chat_history.append({"role": "assistant", "content": image_path})

            yield "", chat_history
        else:
            # استخدام تأثير الكتابة البطئة للرد العادي
            full_response = ""
            for partial in delayed_typing(response):
                full_response = partial
                yield "", chat_history + [{"role": "assistant", "content": full_response}]

            chat_history.append({"role": "assistant", "content": response})

        return "", chat_history
    except Exception as e:
        error_msg = f"❌ حدث خطأ: {str(e)}"
        if not chat_history:
            chat_history = []
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": error_msg})
        return "", chat_history

# ================================
# إنشاء الواجهة
# ================================
with gr.Blocks(theme=gr.themes.Soft(), title="مساعد الأثاث الذكي") as demo:
    gr.Markdown("# 🪑 مساعد الأثاث الذكي مع الذاكرة")
    gr.Markdown("مرحباً! أنا مساعدك الذكي للأثاث. عندي ذاكرة علشان افتكر كل الحاجات اللى بنتكلم فيها!")
    
    with gr.Row():
        with gr.Column(scale=4):
            chatbot_ui = gr.Chatbot(
                elem_id="chatbot",
                type="messages",
                height=500,
                show_copy_button=True,
                placeholder="مرحباً! تقدر تقولي 'أضف كنبة' أو 'شوف اللى ضفت' أو 'المساعدة'",
                label="المحادثة"
            )
            
        with gr.Column(scale=1):
            gr.Markdown("### 🚀 إجراءات سريعة")
            
            show_furniture_btn = gr.Button("🪑 عرض الأثاث", size="sm")
            show_my_items_btn = gr.Button("📋 اللى ضفت", size="sm")
            show_colors_btn = gr.Button("🎨 الألوان", size="sm")
            show_materials_btn = gr.Button("🛠️ المواد", size="sm")
            help_btn = gr.Button("🛟 المساعدة", size="sm")
            clear_btn = gr.Button("🗑️ مسح الكل", size="sm")
    
    with gr.Row():
        msg = gr.Textbox(
            label="اكتب رسالتك هنا...", 
            placeholder="مثال: أضف كنبة حمراء، امسح الكرسي، شوف اللى ضفت، الألوان للكنبة",
            max_lines=2,
            scale=4
        )
        
    with gr.Row():
        submit_btn = gr.Button("إرسال 🚀", variant="primary", size="lg")
        clear_chat_btn = gr.Button("مسح المحادثة ❌", size="lg")
    
    # تخزين حالة المحادثة
    chat_state = gr.State([])
    
    # أحداث الإرسال
    submit_btn.click(
        fn=chat_fn,
        inputs=[msg, chat_state],
        outputs=[msg, chatbot_ui]
    )
    
    msg.submit(
        fn=chat_fn,
        inputs=[msg, chat_state],
        outputs=[msg, chatbot_ui]
    )
    
    # أحداث الإجراءات السريعة
    show_furniture_btn.click(
        fn=handle_quick_action,
        inputs=[gr.Textbox("عرض الأثاث", visible=False), chat_state],
        outputs=[chatbot_ui]
    )
    
    show_my_items_btn.click(
        fn=handle_quick_action,
        inputs=[gr.Textbox("عرض اللى ضفت", visible=False), chat_state],
        outputs=[chatbot_ui]
    )
    
    show_colors_btn.click(
        fn=handle_quick_action,
        inputs=[gr.Textbox("الألوان", visible=False), chat_state],
        outputs=[chatbot_ui]
    )
    
    show_materials_btn.click(
        fn=handle_quick_action,
        inputs=[gr.Textbox("المواد", visible=False), chat_state],
        outputs=[chatbot_ui]
    )
    
    help_btn.click(
        fn=handle_quick_action,
        inputs=[gr.Textbox("المساعدة", visible=False), chat_state],
        outputs=[chatbot_ui]
    )
    
    # أحداث المسح
    def clear_chat_interface():
        clear_chat()
        return None, []
    
    clear_btn.click(
        fn=clear_chat_interface,
        outputs=[chatbot_ui, chat_state]
    )
    
    clear_chat_btn.click(
        fn=clear_chat_interface,
        outputs=[chatbot_ui, chat_state]
    )

# تشغيل الواجهة
if __name__ == "__main__":
    demo.launch(share=True, debug=True)