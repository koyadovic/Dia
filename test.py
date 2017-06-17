
from dia.core import diacore
from dia.models import GlucoseLevel

g = GlucoseLevel(user_pk=1, utc_timestamp=0, mgdl_level=120)
g = diacore.add_glucose_level(g)
print g