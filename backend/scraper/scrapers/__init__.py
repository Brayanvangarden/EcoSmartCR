from .pricesmart import buscar_pricesmart
from .maxipali import buscar_maxipali
from .walmart import buscar_walmart
from .masxmenos import buscar_masxmenos 

TIENDAS = [
    buscar_walmart,
    buscar_masxmenos,
    buscar_maxipali,
    buscar_pricesmart
]