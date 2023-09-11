from datetime import datetime, timedelta

def uuid1_time_to_datetime(time: int) -> datetime:
    if time < 0:
        raise ValueError("Time cannot be negative")
    # Converting 100-nanosecond intervals to microseconds (10^2 nanoseconds = 1 microsecond)
    microseconds = time // 10
    # Base date for UUID v1 timestamps (October 15, 1582)
    base_date = datetime(1582, 10, 15)
    return base_date + timedelta(microseconds=microseconds)
