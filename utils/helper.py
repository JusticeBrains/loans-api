from datetime import timedelta
import calendar

MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def count_working_days(start_date, end_date):
    if start_date and end_date:
        total_days = (end_date - start_date).days + 1
        working_days = 0

        for day in range(total_days):
            current_day = start_date + timedelta(days=day)
            if current_day.weekday() < 5:
                working_days += 1

        return working_days


def generate_calender(year):
        cal = calendar.Calendar()
        year_calender = {}

        for month in range(1, 13):
            month_calender = cal.monthdayscalendar(year, month)
            cleaned_onth_calender = [
                [day for day in week if day != 0] for week in month_calender
            ]
            year_calender[month] = cleaned_onth_calender

        return year_calender

def get_days_in_month(year: int, month: int):
        return calendar.monthrange(year, month)[1]