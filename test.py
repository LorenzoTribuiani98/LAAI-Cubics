from minizinc import Model, Solver, Instance
import numpy as np
import os
from datetime import timedelta

model_path = os.path.join(
        os.path.dirname(__file__),
        "Cube_minimizer.mzn"
    )

model = Model(model_path)
solver = Solver.lookup("gecode")
inst = Instance(solver,model)

inst["cols"] = 10
inst["rows"] = 4
inst["field"] = np.array([1,1,1,1,1,1,0,0,0,0|1,1,1,1,1,1,0,0,0,0|1,1,1,0,1,1,0,0,0,0|1,1,1,0,1,1,0,0,0,0|]
)

out = inst.solve(timeout=timedelta(seconds=300), free_search=True)
print(out.solution)