class DateTimeUtils:
    def __int__(self):
        return

    def add_years(self, start_date, years):
        try:
            return start_date.replace(year=start_date.year + years)
        except ValueError:
            return start_date.replace(year=start_date.year + years, day=28)
