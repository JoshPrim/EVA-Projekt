import rpyc
import pandas as pd
from pandas import DataFrame
import numpy as np


proxy = rpyc.connect('localhost', 37005, config={'allow_public_attrs': True})

tmp = proxy.root.anzahlAusfälle()

print(tmp)
