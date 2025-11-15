import pymysql
from persiantools.jdatetime import JalaliDate
import os


class MigrationBase:
    def __init__(self):
        self.conn = pymysql.connect(
            host="localhost",
            user=os.getenv("mysql_user"),
            passwd=os.getenv("mysql_pass"),
            db=os.getenv("mysql_db"),
        )
        self.cursor = self.conn.cursor()
        "root", "", "healthtwooct"

    def correct_date_system(self, date: str) -> str:
        date = date.replace(" ", "")
        year = ""
        month = "01"
        day = "01"
        dates = (
            date.split("-")
            if "-" in date
            else date.split("_")
            if "_" in date
            else date.split("/")
            if "/" in date
            else date.split(".")
        )
        int_dates = [int(date) for date in dates]
        if len(dates) == 1:
            # only year is available
            year = dates[0] if len(dates[0]) == 4 else "13" + dates[0]
        elif len(dates) == 2:
            # year and month are available
            year_index = 1 if int_dates[1] > int_dates[0] else 0
            month_index = 0 if year_index == 1 else 1
            if len(dates[year_index]) == 2:
                year = "13" + dates[year_index]
            else:
                year = dates[year_index]
            if len(dates[month_index]) == 1:
                month = "0" + dates[month_index]
            else:
                month = dates[month_index]
        else:
            # year and month and day is available
            year_index = 2 if int_dates[2] > int_dates[0] else 0
            day_index = 0 if year_index == 2 else 2
            if dates[day_index] == "31" and int_dates[1] >= 6:
                dates[day_index] = "30"

            year = (
                dates[year_index]
                if len(str(dates[year_index])) == 4
                else "13" + str(dates[year_index])
            )
            month = dates[1] if len(dates[1]) == 2 else "0" + dates[1]
            day = (
                dates[day_index]
                if len(dates[day_index]) == 2
                else "0" + dates[day_index]
            )
        return f"{year}-{month}-{day}"

    def print_progress(self, index, total, optional_text=""):
        percent = (index + 1) / total * 100
        print(f"\rDone: {percent:.2f}% {optional_text}", end="")

    def character_replace(self, text: str):
        return text.replace("ي", "ی").replace("ك", "ک")

    def convert_persian_date(self, pdate: str):
        return JalaliDate.fromisoformat(pdate).to_gregorian().isoformat()

    def query(self, query):
        self.cursor.execute(query)
        # replace characters
        rows = self.cursor.fetchall()
        new_rows = []
        for row in rows:
            new_row = [x if bool(x) else None for x in row]
            new_row = [self.character_replace(str(x)) if x else x for x in new_row]
            new_rows.append(new_row)
        return new_rows
