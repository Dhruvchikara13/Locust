import os,sys
#sys.path.append(Root_Dir)
Root_Dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Root path is-", Root_Dir)
Application_folder = os.path.join(Root_Dir, "InsuranceWeb")
sys.path.append(Root_Dir)

from InsuranceWeb.CombinedScript_SeperateClasses import MainAutoQuote, MainAgentLookup
from locust import HttpUser, constant, constant_pacing



# Once script is created for a particular flow, import that script in a new fresh file.
# For each script(that contains the flow) create a  HTTP class with fixed_count as per your requuirement.
# Below we are importing 2 scripts- MainAutoQuote and MainAgentLookup that has all the functionality. Here we are only calling them.
# Each HTTP class below refers to one business flow


class Main1(HttpUser):
    tasks = [MainAutoQuote]
    host = "http://localhost:9090"
    wait_time = constant_pacing(2)
    fixed_count = 5


class Main2(HttpUser):
    tasks = [MainAgentLookup]
    host = "http://localhost:9090"
    wait_time = constant_pacing(10)
    fixed_count = 6
