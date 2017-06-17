
from dia.core import diacore
from dia.models import Trait, TraitKind



print diacore.get_traits(1, kind=TraitKind.HEIGHT_CM, limit=1)[0]
