from minizinc import Model, Solver, Instance
import numpy as np
from tqdm import tqdm
import h5py
from Paradigms.Q_table.Q_table import *

load_table()
q_table_solve({}, [[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]], 0)





