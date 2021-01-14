from dateutil import relativedelta as rdelta
from datetime import date
d1 = date(2001,5,1)
d2 = date(2012,1,1)
rd = rdelta.relativedelta(d2,d1)
print("{0.years} years and {0.months} months".format(rd))
print (date(2001,5,1))
