from db.migration.a1_patient import DBMigration as PatientMigration
from db.migration.a2_medical_tests import DBMigration as MedicalTestMigration
from db.migration.a3_medicine_prescriptions import (
    Migration as MedicinePrescriptionMigration,
)
from db.migration.a4_impressions import DBMigration as ImpressionMigration
from db.migration.a5_medical_imaging import DBMigration as MedicalImagingMigration
from db.migration.a6_referrals import DBMigration as ReferralMigration
from db.migration.a7_thyroid import DBMigration as ThyroidMigration
from db.migration.a8_visit import DBMigration as VisitMigration
from db.migration.a9_basic_history import DBMigration as BasicHistoryMigration
from db.migration.a10_apps import DBMigration as AppointmentMigration
from db.migration.a11_insulin_presc import DBMigration as InsulinMigration

# print("==== PATIENTS ====")
# a1 = PatientMigration()
# a1.import_patients()

print("==== Medical Tests ====")
a2 = MedicalTestMigration()
# a2.import_labs()
# a2.import_metrics()
a2.import_tests_result_groups(quartile=1)
a2.import_tests_result_groups(quartile=2)
a2.import_tests_result_groups(quartile=3)
a2.import_tests_result_groups(quartile=4)

print("==== medicine prescription ====")
a3 = MedicinePrescriptionMigration()
# a3.import_drugs()
a3.import_medicine_prescs()
# a3.import_next_visits()

print("==== impression ====")
a4 = ImpressionMigration()
# a4.import_impressions_titles()
# a4.import_impressions_titles_containing_comma()
a4.import_impressions()

print("==== imagings ====")
a5 = MedicalImagingMigration()
# a5.import_imaging_centers()
# a5.import_imaging_titles()
a5.import_imaging_results()

print("==== referrals ====")
a6 = ReferralMigration()
a6.import_refferals()

print("==== thyroid ====")
a7 = ThyroidMigration()
a7.import_thyroid()

# print("==== VISIT ====")
# a8 = VisitMigration()
# a8.import_visit()

print("==== Basic History ====")
a9 = BasicHistoryMigration()
a9.import_features()
a9.import_stories()

print("==== Appointments ====")
a10 = AppointmentMigration()
a10._import()

print("==== Insulin ====")
a11 = InsulinMigration()
a11.import_insulin()
a11.import_plans()
