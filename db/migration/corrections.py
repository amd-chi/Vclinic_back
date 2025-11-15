from db.migration.base import MigrationBase


tables = ["cons", "examin", "imp", "para", "pmh", "vdrug", "visited", "v_test"]
mappings = [
    [7724, 6416],
    [7796, 1300],
    [8382, 7805],
    [8944, 5915],
    [9595, 6595],
    [9862, 6572],
    [12212, 5777],
    [12378, 9815],
    [13367, 8741],
    [13560, 7734],
    [13792, 12831],
    [14814, 5047],
    [15765, 7500],
    [16235, 16234],
    [16281, 16280],
    [16323, 11832],
    [17035, 10160],
    [17155, 3789],
    [17427, 13765],
    [17557, 15536],
    [17592, 16747],
    [18044, 10836],
    [18050, 5731],
]

db = MigrationBase()

# ساختن mapping به‌صورت دیکشنری
mapping_dict = {}
for old, new in mappings:
    if old not in mapping_dict:
        mapping_dict[old] = (
            new  # فقط اولین مقدار جایگزین برای هر old_value در نظر گرفته می‌شود
        )

# ساخت کوئری CASE WHEN
cases = "\n".join(
    [f"WHEN idnum = {old} THEN {new}" for old, new in mapping_dict.items()]
)
ids = ", ".join(map(str, mapping_dict.keys()))


def run():
    for table in tables:
        try:
            query = f"""
            UPDATE {table}
            SET idnum = CASE
                {cases}
                ELSE idnum
            END
            WHERE idnum IN ({ids});
            """
            db.query(query)
            print(table, "ok")
        except Exception:
            print(table)
            continue
