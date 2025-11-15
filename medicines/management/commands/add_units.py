from django.core.management.base import BaseCommand

from medical_tests.models import MetricUnit


class Command(BaseCommand):
    help = "Imports some units it into Unit model"

    def handle(self, *args, **kwargs):
        units = [
            "mmhg",
            "million cells/μL",  # شمارش سلول‌ها (مثل RBC)
            "thousand cells/μL",  # شمارش گلبول سفید (WBC)
            "g/dL",  # غلظت هموگلوبین (Hb)
            "fL",  # حجم متوسط سلولی (MCV)
            "mg/dL",  # گلوکز، کلسترول، کلسیم، تری‌گلیسرید و غیره
            "μg/dL",  # کورتیزول، ویتامین D
            "ng/mL",  # فریتین، ویتامین B12، تستوسترون
            "pg/mL",  # استروژن، پروژسترون
            "U/L",  # آنزیم‌ها (ALT, AST, ALP)
            "IU/L",  # ایمونوگلوبولین‌ها (C3, C4)
            "mIU/mL",  # هورمون‌ها (TSH, FSH, LH)
            "μU/mL",  # هورمون تیروئید
            "mEq/L",  # الکترولیت‌ها (K, Na, Cl)
            "mm/hr",  # سرعت رسوب گلبول‌های قرمز (ESR)
            "mg/24h",  # آنالیز ادرار 24 ساعته
            "mL/min",  # فیلتراسیون گلومرولی (GFR, eGFR)
            "ng/dL",  # هورمون‌های تیروئید آزاد (Free T3, Free T4)
            "mg/L",  # پروتئین ادرار
            "mg/g",  # نسبت کراتینین به پروتئین ادرار
            "ng/L",  # مارکرهای توموری (PSA)
            "μmol/L",  # اوریک اسید، کراتینین
            "mOsm/kg",  # اسمولالیته ادرار
            "ng/24h",  # متانفرین و نورمتانفرین در ادرار 24 ساعته
            "μg/mg",  # نسبت میکروآلبومین به کراتینین
            "ng/μL",  # برخی هورمون‌ها
            "mIU/L",  # هورمون‌های بارداری و برخی ایمونوآسی‌ها
            "cm/s",  # سرعت جریان خون در داپلر
            "dB",  # سطح شنوایی در ادیومتری
            "mEq/24h",  # الکترولیت‌ها در ادرار 24 ساعته
            "IU/mL",  # ایمونوگلوبولین‌ها
            "mg/dL",  # قند خون بعد از 2 ساعت (OGTT)
            "nmol/L",  # هورمون‌های استروئیدی
            "μmol/24h",  # ترکیبات ادرار (مثل اگزالات)
            "mg/kg",  # نسبت دارو به وزن بدن
            "pg/mL",  # برخی از هورمون‌های استروئیدی
            "μg/L",  # برخی مواد معدنی (مثل روی و مس)
            "pmol/L",  # برخی از هورمون‌های پپتیدی
        ]

        for unit in units:
            MetricUnit.objects.get_or_create(name=unit)

        self.stdout.write(self.style.SUCCESS("units successfully imported"))
