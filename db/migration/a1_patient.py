from db.migration.base import MigrationBase
from patient.models import Patient
from persiantools.jdatetime import JalaliDate
from django.db import transaction
from persian_gender_detection import get_gender


class DBMigration(MigrationBase):
    def __init__(self):
        super().__init__()

    def map_insurance(self, text):
        if text == "تامین اجتماعی":
            return "tamin"
        elif text == "نیروهای مسلح":
            return "military"
        elif text == "سلامت":
            return "salamat"
        elif text == "بانکها":
            return "bank"
        elif text == "آزاد":
            return "azad"
        else:
            return None

    def import_patients(self, ids: list = None):
        rows = self.query(
            "select * from iden"
            if not ids
            else "select * from iden where id in ({})".format(
                ",".join([str(id) for id in ids])
            )
        )
        lenr = len(rows)
        print(lenr)
        patients_saved = 0
        ignored_patients = 0
        with transaction.atomic(), open(
            "db/migration/logs/1.log", "w", encoding="utf-8"
        ) as f:
            for row in rows:
                if Patient.objects.filter(id=row[0]).exists():
                    continue
                patient = Patient()
                patient.id = row[0]
                patient.first_name = row[1].strip() if row[1] else None
                if patient.first_name:
                    sex = get_gender(patient.first_name)
                    patient.sex = (
                        "F" if sex == "FEMALE" else "M" if sex == "MALE" else None
                    )
                patient.last_name = row[2].strip() if row[2] else None
                patient.national_id = row[4]
                if not patient.last_name and not patient.national_id:
                    ignored_patients += 1
                    f.write(f"problem {str(row)} \n")
                    continue
                patient.refferal_reason = row[6]
                patient.height = row[9]
                patient.weight = row[10]

                patient.telephone = row[11]
                patient.phone_number = (
                    f"0{row[12]}" if (bool(row[12]) and row[0] != "0") else row[12]
                )
                patient.address = row[13]
                patient.city = row[14]
                patient.referer = row[15]
                if row[16] != "0000-00-00":
                    try:
                        patient.birth_date = self.convert_persian_date(row[16])
                    except Exception:
                        year = row[16].split("-")[0]
                        if year != "0000":
                            patient.birth_date = (
                                JalaliDate.fromisoformat(f"{year}-01-01")
                                .to_gregorian()
                                .isoformat()
                            )
                        else:
                            patient.birth_date = None
                        print(
                            f"malform date: in converting date {row[16]}=>{patient.birth_date}"
                        )
                else:
                    patient.birth_date = None
                patient.education = self.map_edu_choices(row[19])
                patient.occupation = None
                patient.insurance_company = self.map_insurance(row[23])
                if row[4] and Patient.objects.filter(national_id=row[4]).exists():
                    ignored_patients += 1
                    f.write(f"national_id duplicate: {row}\n")
                    continue
                patient.save()
                patients_saved += 1
                self.print_progress(patients_saved, lenr)

        print(f"\nAdded {patients_saved} patients | {ignored_patients} ignored")

    def get_distinct_edu2(self):
        rows = self.query("select DISTINCT edu from iden")
        items = set()
        for row in rows:
            items.add(row[0])
        return items

    def map_edu_choices(self, item: str):
        if item in [
            "بی سواد",
            "بیسواد",
        ]:
            return "illiterate"
        if item in [
            "ابندایی",
            "دبستان",
            " ششم ابتدایی",
            "ابتدایی",
            "لبتدایی",
            "ابتدايي",
            "لبتدايي",
            "پیش دبستان",
            "دانش اموز",
            "اول ابتدایی",
            "ششم",
            "ششم ابتداعی",
            "ششم ابتدایی",
            "ایتدایی",
            "دانش آموز",
            "دانش اموز",
            "پنجم",
            "چهارم ابتدایی",
            "دوم دبستان",
            "سوم",
        ]:
            return "elementary"
        elif item in [
            "سیکل",
            "راهنمایی",
            "راهنمایی",
            "کلاس هفتم",
            "متوسطه",
            "سیل",
            "سیکل",
        ]:
            return "secondary"
        elif item in [
            "دبیرستان",
            " دانشجو",
            "اول دبیرستان",
            "راهنمای",
            "سوم راهنمایی",
            "دهم",
            "دوازدهم",
            "پیش دانشگاهی",
            "دبیرستان",
            "یاذدهم",
            "نهم",
            "هشتم ",
            "هفتم",
            "زیر دیپلم",
        ]:
            return "high_school"
        elif item in [
            "دپیلم",
            " دیپلم",
            "دیبلم",
            "دیپام",
            "دیپبلم",
            "دیپلم",
            "دیپلم فنی",
            "دیچلم",
            "یپلم",
            "دیپام",
            "روزنامه نگار",
            "پیش دانشگاهی" "اول نظری",
            "دبپلم",
            "روحانی",
            "دپیلم",
            "حوزوی",
        ]:
            return "diploma"
        elif item in [
            " فوق دیپلم",
            "فوق دیپبلم",
            "فوق دیپلم",
            "تربیت معلم",
            "فوقد دیپلم",
            "قوق دیپلم",
            "فئوق دیپلم",
            "فقو دیپلم",
            "فوق  دیپلم",
            "فوق ددیپلم",
            "فوق دیپلم خیاطی",
            "فوق دیپلم زبان انگلیسی",
            "فوق دیپلم معماری",
            "فوق دیپلکم",
            "فوق ذیپلم",
            "فوق دیبلم",
            "فوق دیپبلم",
            "فوق دیپلم",
            "کاردانی",
            "فوف دیپلم",
            "دبیر",
        ]:
            return "associate"
        elif item in [
            "داتنشجو",
            "ایسانس",
            "ایسانس حسابداری",
            "داشنجو",
            "لیسانس",
            " دانشجو",
            "کارشناسی",
            "دانشجو حسابداری",
            "دانشجو حقوق",
            "دانشجو لیسانس",
            "لبسانس",
            "لبیسانس",
            "لسانس",
            "لیاسانس",
            "لیساتس",
            "لیساتنس",
            "لیساس",
            "لیسالنس",
            "لیسان",
            "لیسانس",
            "لیسانس ادبیات",
            "لیسانس اقتصاد",
            "لیسانس الکترونیک",
            "لیسانس بازرکانی",
            "لیسانس بازرگانی",
            "لیسانس بانکداری",
            "لیسانس بیولوژی",
            "لیسانس تغذیه",
            "لیسانس حسابداری",
            "لیسانس حقوق ",
            "لیسانس رادیولوژی",
            "لیسانس روانشناسی",
            "لیسانس ریاضی",
            "لیسانس زبان",
            "لیسانس شیمی",
            "لیسانس صنایع",
            "لیسانس طراحی لباس",
            "لیسانس عمران",
            "لیسانس فیزیک",
            "لیسانس مامایی",
            "کارشناس",
            "کارشناس آزمایشگاه",
            "کارشناس زبان انگایسی",
            "کارشناس شیمی",
            "کارشناس ماما",
            "کارشناس مامایی",
            "کارشناس میکروبیولوژی",
            "کارشناس پرستاری",
            "کارشناسی",
            "کارشناسی ادبیات فارسی",
            "کارشناسی ارشد",
            "کارشناسی ارشد برق",
            "کارشناسی زمین شناسی",
            "کارشناسی مهندسی ",
            "کارشناسی میکروبیولوژی",
            "لیسانس مدیریت",
            "لیسانس مدیریت بازرگانی",
            "لیسانس مدیریت یازرگانی",
            "لیسانس معماری",
            "لیسانس مهندسی",
            "لیسانس ژنتیک ",
            "لیسانس کامپیوتر",
            "لیسانس گرافیک",
            "لییسانس",
            "دانشجو معماری",
            " کارشناسی ماما",
            " لیسانس",
            "دانشچو",
            "ماما",
            "مامایی",
            "مهندس",
            "مترجم زبان",
            "مهندس آی تی ",
            "عمران",
            "مهندس",
            "مهندس آی تی ",
            "کازشناسی",
            "مهندس الکترونیک",
            "مهندس شیمی",
            "مهندس عمران",
            "مهندس متالوژی",
            "مهندس مکانیک",
            "مهندسی",
            "مهندسی برق",
            "مهندسی مکانیک",
            "مهندسی پزشکی",
        ]:
            return "bachelor"
        elif item in [
            "فوق",
            "دانشجو فوق",
            "دانشجوی حقوق ",
            "کازشناسی ارشد",
            "کاشناسی ارشد",
            "دانشجو ارشد",
            "داشجو ارشد",
            "وق لیسانس",
            "ارشد حقوق",
            "ارشد مامایی",
            "روانشناس",
            "ارشد مدیریت",
            "فو ق لیسانس",
            "فوق  لیسانس",
            "فو لیسانس",
            "فوف لیسانس",
            "ارشد معماری",
            "فوق لسانس",
            "فوق لیسانس ادبیات انگلیسی",
            "فوق لیسانس شیمی",
            "فوق لیسانس مامایی",
            "فوق لیسانس مدیریت",
            "فوق لیسانس مدیریت بازرگانی",
            "فوق لیسانس معماری",
            "فوق لیسلنس",
            "فوق لییسانس",
            "فوق یسانس",
            "فوق لیانس",
            "فوق لیساتس",
            "فوق لیساس",
            "وکیل ",
            "فوق لیسانس",
            "فق لیسانس",
            "ارشد مهندسی پزشکی",
            "ارشد کارمند",
            "ارشدئ",
            "ازشد",
            "ارشد",
            " ارشد",
            " فوق لیسانس",
        ]:
            return "master"
        elif item in [
            " داروساز",
            "تخصص دندانپزشکی ",
            "جراح گوش",
            "دامپزشک",
            "داروساز",
            "دانشجو پزشکی",
            "تکنسین دارویی",
            "دانشجو دکترا",
            "پی اچ دی",
            "دانشجو دکتری",
            "دانشچو دامپزشکی",
            "دکتر داروساز",
            "دکتر",
            "دندانپزشک",
            "دنشجوی دکترا",
            "دکترا",
            "دکترا برق",
            "دکترا تخصص",
            "دکترا حرکت",
            "دکترا حقوق ",
            "دکترا داروسازی",
            "دکترا دندانپزشکی",
            "دکترا روانشناسی",
            "دکترا شیمی",
            "دکترا طب",
            "دکترا مدیریت",
            "دکتراداروسازی",
            "دکترای تخصصی",
            "دکترای حرفه ای پزشکی",
            "دکترای سیاسی",
            "دکترای عمران",
            "دکترای عمومی",
            "دکترای مهندسی برق",
            "دکتری",
            "رزیدنت",
            "رزیدنت اطفال",
            "فوق تخصص",
            "متخصص",
            "متخصص اطفال",
            "متخصص اعصاب وروان",
            "متخصص ایمونولوژی",
            "متخصص جراحی",
            "متخصص داخلی",
            "متخصص زنان",
            "متخصص طب اورزانس",
            "متخصص طب اورژانس",
            "متخصص طب پیشگیری",
            "متخصص عفونی",
            "متخصص قلب",
            "پزشک",
            "پزشک عمومی",
            "پزشک متخصص",
            "پی اچ دی شیمی",
            "متخصص مغز و اعصاب",
            "متخصص پزشکی قانونی",
            "متخصص پوست",
            "متخصص کودکان",
        ]:
            return "phd"
        else:
            return None

    def get_duplicate_national_id(self):
        return self.query(
            "SELECT id, national_id, COUNT(*) FROM iden GROUP BY national_id HAVING COUNT(*) > 1;"
        )

    def set_duplicates_null_national_id(self):
        nids = [
            "1754636802",
            "0323798411",
            "3240253615",
            "1460962036",
            "0021594899",
            "4710270953",
            "0441345883",
            "0045058611",
            "0530395401",
            "0049150561",
            "0081648601",
            "0047207620",
            "0050345079",
            "0016103033",
            "3070930417",
            "5709736104",
            "0040840141",
            "2160074179",
            "0042509874",
            "0020712146",
            "4431448268",
            "0530395401",
            "0383711037",
            "0439297605",
            "0450987272",
            "0570151120",
            "1262215455",
            "4431448268",
        ]
        # check if all exist in iden table
        for nid in nids:
            dups = self.query(f"SELECT * FROM iden WHERE national_id = '{nid}'")
            if len(dups) > 1:
                self.query(
                    f"UPDATE iden SET national_id = NULL WHERE id = {dups[0][0]}"
                )
                print("duplicate found and replaced with null")


# a = DBMigration()
# a.import_patients()
