from itertools import product

DAYS_OF_WEEK = ["Mon", "Tues", "Wed", "Thu", "Fri"]
OH_TIMES = [
    "10-11 AM",
    "11-12 PM",
    "12-1 PM",
    "1-2 PM",
    "2-3 PM",
    "3-4 PM",
    "4-5 PM",
    "5-6 PM",
    "6-7 PM",
]
OH_CHOICES = [
    (choice, choice)
    for choice in [" ".join(oh) for oh in product(DAYS_OF_WEEK, OH_TIMES)] + ["N/A"]
]
