"""Quick demo — generates a sample Jadhagam without user input."""

from datetime import date, time
from jadhagam import generate_jadhagam, print_jadhagam

# Example: born 15 August 1990, 06:30 AM, Chennai
data = generate_jadhagam(
    name="ராமன் (Raman)",
    birth_date=date(1990, 8, 15),
    birth_time=time(6, 30),
    birth_place="Chennai, Tamil Nadu",
)

print_jadhagam(data)
