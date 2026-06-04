# Mock flatlib Datetime

class Datetime:
    def __init__(self, date: str, time: str, utcoffset = 0.0):
        self.date = date
        self.time = time
        # Convert timezone string like '+05:30' to float hours
        if isinstance(utcoffset, str):
            sign = 1
            if utcoffset.startswith("-"):
                sign = -1
                utcoffset = utcoffset[1:]
            elif utcoffset.startswith("+"):
                utcoffset = utcoffset[1:]
            
            if ":" in utcoffset:
                parts = utcoffset.split(":")
                try:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    utcoffset = sign * (hours + minutes / 60.0)
                except ValueError:
                    utcoffset = 0.0
            else:
                try:
                    utcoffset = sign * float(utcoffset)
                except ValueError:
                    utcoffset = 0.0
        self.utcoffset = utcoffset

    def __str__(self):
        return f"{self.date} {self.time} (UTC {self.utcoffset:+})"
