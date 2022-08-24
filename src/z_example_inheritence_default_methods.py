from dataclasses import dataclass


@dataclass
class Person:
    name: str = "John Susanto"
    age: int = 3

    def __str__(self) -> str:
        return str(self.name) + "_asda"

    def change_toy(self):
        self.toys = "changed"


@dataclass
class Child(Person):
    toys: str = "Playdough"


p = Child(name="baby")
p.change_toy()
print(p.toys)
