"""
import sched, time

s = sched.scheduler(time.time, time.sleep)


def print_time(a="default"):
    print("From print_time", time.time(), a)


def print_some_times():
    print(time.time())
    s.enter(10, 1, print_time)
    s.enter(5, 2, print_time, argument=("positional",))
    s.enter(5, 1, print_time, kwargs={"a": "keyword"})
    s.run()
    print(time.time())


print_some_times()
"""
from dataclasses import dataclass, field


@dataclass
class parent:
    att1: int
    att2: int = field(init=False, default=3)


@dataclass
class child(parent):
    att3: str


c = child(1, att3="asd")
p = parent(1)
print(type(c))
print(type(p))

print(isinstance(c, parent))
