from datetime import date, timedelta
import re
import holidays
import xml.etree.ElementTree as ET


def get_euro_rate_from_day2(d: date):
    file_path = f"static/nbrfxrates{d:%Y}.xml"
    context = ET.iterparse(file_path, events=("start", "end"))
    rate = 0
    line = 0
    for event, elem in context:
        if event == "start" and elem.tag == "Cube":
            print(elem.attrib)
            if elem.attrib.get("date") == f"{d:%Y-%m-%d}":
                for rate in elem.findall("Rate"):
                    if rate.attrib.get("currency") == "EUR":
                        rate = float(rate.text)
                        break
    if rate == 0:
        print(f"no rate found for {d:%Y-%m-%d}")
        # rate = get_euro_rate_from_day(d - timedelta(days=1))
    return rate

def get_euro_rate_from_day(d: date):
    file_path = f"static/nbrfxrates{d:%Y}.xml"

    with open(file_path, "r", encoding="utf-8") as response:
        xml = response.read()
        date_format = f'date="{d:%Y-%m-%d}"'
        look_for_rate = False
        rate = 0
        
        for xml_line in xml.splitlines():
            if date_format in xml_line: 
                look_for_rate = True
            if look_for_rate and "EUR" in xml_line:
                match = re.search(r'<Rate currency="EUR">([\d.]+)</Rate>', xml_line)
                rate = float(match.group(1))
                break
    
    if rate == 0:
        rate = get_euro_rate_from_day2(d - timedelta(days=1))
    
    return rate


def get_previous_working_day(requested_date: date) -> date:
    while True:
        requested_date = requested_date - timedelta(days=1)
        if not is_public_holiday(requested_date):
            return requested_date


def is_public_holiday(requested_date: date) -> bool:
    ro_holidays = holidays.RO(years=requested_date.year)
    if requested_date in ro_holidays:
        return True
    else:
        if requested_date.weekday() >= 5:
            return True
    return False


def generate_data_for_date(requested_date: date) -> dict:
    ro_holidays = holidays.RO(years=requested_date.year)
    public_holiday = False
    public_holiday_name = None
    if requested_date in ro_holidays:
        public_holiday = True
        public_holiday_name = ro_holidays.get(requested_date)
    else:
        if requested_date.weekday() >= 5:
            public_holiday = True
            public_holiday_name = "Weekend"
    return {
        "date": requested_date.isoformat(),
        "weekday": requested_date.strftime("%A"),
        "public_holiday": public_holiday,
        "public_holiday_name": public_holiday_name,
        "euro_rate": get_euro_rate_from_day(requested_date),
        "previous_working_day": get_previous_working_day(requested_date).isoformat(),
    }


def get_last_day_of_month(month: int, year: int) -> date:
    last_day = 31
    one_day = timedelta(days=1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - one_day
    else:
        last_day = date(year, month + 1, 1) - one_day
    # print(f"Last day of month {month} from {year} is: {last_day: %B(%m)/%d %0A}")
    return last_day


if __name__ == "__main__":
    month = 12
    year = 2024
    dl = get_last_day_of_month(month, year)
    dd = get_previous_working_day(get_last_day_of_month(month,year));
    print(f"{month}/{year} last day is {dl:%A, %d-%m-%Y} and the rate is {get_euro_rate_from_day(dl)}")
    print(f"{month}/{year} previous is {dd:%A, %d-%m-%Y} and the rate is {get_euro_rate_from_day(dd)}")


