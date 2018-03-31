import datetime
import json


class FiscalYear:
    def __init__(self, year, start, month_lengths):
        self.year = year
        self.start = start
        self.end = start + datetime.timedelta(days=363)
        self.fiscal_months = []

        start_of_month = start
        for n, length in enumerate(month_lengths,  1):
            end_of_month = start_of_month + datetime.timedelta(days=length-1)
            self.fiscal_months.append(FiscalMonth(n, start_of_month, end_of_month))
            start_of_month = end_of_month + datetime.timedelta(days=1)

    def month_of_date(self, date):
        for f_m in self.fiscal_months:
            if f_m.contains(date):
                return f_m

    def current_fiscal_month(self):
        return self.month_of_date(datetime.datetime.today())

    def month(self, n):
        return self.fiscal_months[n-1]

    def __str__(self):
        s = ''
        for x in range(1, 13):
            s += str(self.month(x).start) + '\n'
            s += str(self.month(x).end) + '\n' + '\n'
        return s


class FiscalMonth:
    def __init__(self, fiscal_month_number, start, end):
        self.number = fiscal_month_number
        self.start = start
        self.end = end
        self.length = 35 if fiscal_month_number in [2, 5, 8, 11] else 28

    def week(self, n):
        s = self.start + datetime.timedelta(days=(7*n-7))
        return FiscalWeek(n, s)

    def contains(self, date):
        s = self.start.year*10000 + self.start.month*100 + self.start.day
        e = self.end.year*10000 + self.end.month*100 + self.end.day
        d = date.year*10000 + date.month*100 + date.day
        return s <= d <= e


class FiscalWeek:
    def __init__(self, fiscal_week_number, start):
        self.number = fiscal_week_number
        self.start = start
        self.end = start + datetime.timedelta(days=6)

    def contains(self, date):
        s = self.start.year*10000 + self.start.month*100 + self.start.day
        e = self.end.year*10000 + self.end.month*100 + self.end.day
        d = date.year*10000 + date.month*100 + date.day
        return s <= d <= e


def restore_default_config():
    config = dict(
        FISCAL_YEAR=2018,
        START_DATE=dict(
            YEAR=2018,
            DAY=4,
            MONTH=2,
        ),
        MONTH_LENGTH=[28, 35, 28, 28, 35, 28, 28, 35, 28, 28, 35, 28]
    )
    with open('config/FISCAL_YEAR.config', 'w+') as file:
        json.dump([config], file, indent=3)

    print(config)


def load_config():
    with open('config/FISCAL_YEAR.config', 'r') as file:
        return json.loads(file.read())


def add_year_to_config(data):
    config = load_config()
    if data.get('FISCAL_YEAR') < config[0].get('FISCAL_YEAR'):
        return {'Error: Cannot add a past fiscal year'}
    elif data.get('FISCAL_YEAR') == config[0].get('FISCAL_YEAR'):
        config[0]['START_DATE'] = data.get('START_DATE')
        config[0]['MONTH_LENGTH'] = data.get('MONTH_LENGTH')
    else:
        config = [data] + config
    with open('config/FISCAL_YEAR.config', 'w+') as file:
        json.dump(config, file, indent=3)
    return None


def current_fiscal_year():
    config = load_config()
    previous_known_year = config[0].get('FISCAL_YEAR')
    start = config[0].get('START_DATE')
    y = start.get('YEAR')
    m = start.get('MONTH')
    d = start.get('DAY')
    length = sum(config[0].get('MONTH_LENGTH'))
    delta = (datetime.datetime.today() - datetime.datetime(year=y, month=m, day=d)+datetime.timedelta(days=length))
    years_since_previous_known_year = int(delta.days/364)-1
    return previous_known_year + years_since_previous_known_year


def start_of_fiscal_year(year):
    config = load_config()
    for x in config:
        if x.get('FISCAL_YEAR') == year:
            s = x.get('START_DATE')
            return datetime.datetime(year=s.get('YEAR'), month=s.get('MONTH'), day=s.get('DAY'))

    previous_known_year = config[0].get('FISCAL_YEAR')
    start = config[0].get('START_DATE')
    y = start.get('YEAR')
    m = start.get('MONTH')
    d = start.get('DAY')
    previous_known_year_length = sum(config[0].get('MONTH_LENGTH'))
    years_since_previous_known_year_start = year-previous_known_year
    if year > previous_known_year:
        days = previous_known_year_length + (years_since_previous_known_year_start-1)*364
    else:
        days = years_since_previous_known_year_start * 364
    return datetime.datetime(year=y, month=m, day=d) + datetime.timedelta(days=days)


def month_lengths_of_fiscal_year(year):
    config = load_config()
    for x in config:
        if x.get('FISCAL_YEAR') == year:
            return x.get('MONTH_LENGTH')
    return [28, 35, 28, 28, 35, 28, 28, 35, 28, 28, 35, 28]


def week_number_of_fiscal_month(date):
    fy_number = current_fiscal_year()
    fy_start = start_of_fiscal_year(fy_number)
    fy_length = month_lengths_of_fiscal_year(fy_number)
    fy_this_year = FiscalYear(year=fy_number, start=fy_start, month_lengths=fy_length)

    n = [
            x for x in range(1, 6)
            if fy_this_year.month_of_date(date).week(x).contains(date)
    ]
    return n[0]


if __name__ == "__main__":
    # Create fiscal year for 2018 with start date February 4 2018
    d = dict(
        FISCAL_YEAR=2018,
        START_DATE=dict(
            YEAR=2018,
            DAY=4,
            MONTH=2,
        ),
        MONTH_LENGTH=[28, 35, 28, 28, 35, 28, 28, 35, 28, 28, 35, 28]
    )

    n = week_number_of_fiscal_month(datetime.datetime.now()+datetime.timedelta(days=5))
    print(n)





