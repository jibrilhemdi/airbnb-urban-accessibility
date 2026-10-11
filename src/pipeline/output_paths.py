"""Semantic paths for aggregate research outputs; row-level records stay in SQL."""
from pathlib import Path
import re
from src.ingestion.common import PROJECT_ROOT
FAMILIES = frozenset({'data','airbnb_sample','area_context','geography','euclidean_accessibility','walking_accessibility','accessibility','analysis_dataset','validation','primary_models','income_robustness','robustness','reporting','reproducibility','official_transport'})
def output_file(kind: str, family: str, name: str) -> Path:
    if kind not in {'tables','figures'} or family not in FAMILIES:
        raise ValueError('Unknown output kind or semantic family')
    if Path(name).name != name or name in {'','.','..'}:
        raise ValueError('Output name must be a basename')
    if re.search(r'(?i)(ph'+r'ase\d*|post'+r'completion|pre_'+r'freeze)',name):
        raise ValueError('Historical sequencing is not allowed in current output names')
    return PROJECT_ROOT/'outputs'/kind/family/name
class OutputDirectory:
    def __init__(self,kind: str,family: str):
        self.kind,self.family=kind,family
        self.path=output_file(kind,family,'.keep').parent
    def __truediv__(self,name: str)->Path:
        return output_file(self.kind,self.family,name)
    def mkdir(self,*args,**kwargs): self.path.mkdir(*args,**kwargs)
    def glob(self,pattern: str): return self.path.glob(pattern)
