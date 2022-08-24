from croniter import croniter
from datetime import datetime

base = datetime(2010, 1, 25, 4, 46)
iter = croniter("*/5 * * * *", base)  # every 5 minutes
print(iter.start_time)
print(type(iter))
print(iter.expanded)
print("start - ", base)
print("curr - \t", iter.get_current(datetime))

print("1 - \t", iter.get_next(datetime))  # 2010-01-25 04:50:00
print("2 - \t", iter.get_next(datetime))
print(iter.get_current(datetime))
print("start extracted - ", datetime.utcfromtimestamp(iter.start_time))
print("start extracted - ", datetime.fromtimestamp(iter.start_time))
