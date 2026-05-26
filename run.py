import os
import sys
import runpy

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import dev.user_interface.tools.q_wrapper

runpy.run_module("dev.core.aeroflow", run_name="__main__")