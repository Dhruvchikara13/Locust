from locust import SequentialTaskSet, HttpUser, task, constant, events
import re
from locust.exception import StopUser

class AgentLookup(SequentialTaskSet):
    def __init__(self, parent):
        super().__init__(parent)
        self.cor_jessionid = ""
        self.cor_viewState = ""
        self.cor_usersessionID = ""

    def on_start(self):
        self.client.cookies.clear()
        text_check = "Select a Service or login"
        with self.client.get("/InsuranceWebExtJS/index.jsf", name="Launch", catch_response=True) as response:
            if text_check in response.text:
                response.success()
                try:
                    cor_viewState = re.findall("j_id\d+:j_id\d+", response.text)
                    self.cor_viewState = cor_viewState[0]
                    # print("ViewStat is",self.cor_viewState)
                except AttributeError:
                    self.cor_viewState = ""
            else:
                response.failure("Text Check not found")
        self.cor_jessionid = response.cookies["JSESSIONID"]

        payload = {
            "login-form": "login-form",
            "login-form:email": "john@test.com",
            "login-form:password": "password",
            "login-form:login.x": "43",
            "login-form:login.y": "10",
            "javax.faces.ViewState": self.cor_viewState
        }
        with self.client.post("/InsuranceWebExtJS/index.jsf", data=payload, cookies={"JSESSIONID": self.cor_jessionid},
                              name="Login", catch_response=True) as response:
            if "Logged in as" in response.text:
                response.success()
            else:
                response.failure("Login failed")
        self.cor_usersessionID = response.cookies["UserSessionFilter.sessionId"]
        # print("UserSessionid is",self.cor_usersessionID)

    @task
    def agent_lookup(self):
        with self.client.get("/InsuranceWebExtJS/agent_lookup.jsf", cookies={"JSESSIONID": self.cor_jessionid,
                                                                           "UserSessionFilter.sessionId": self.cor_usersessionID},
                             name="T01_AgentLookupTab", catch_response=True) as response:
            if "Get in touch with an Insurance Co. agent" in response.text:
                response.success()
                try:
                    cor_viewState = re.findall("j_id\d+:j_id\d+", response.text)
                    self.cor_viewState = cor_viewState[0]
                    # print("ViewStat is", self.cor_viewState)
                except AttributeError:
                    self.cor_viewState = ""
            else:
                response.failure("Text check not found>>Automobile Instant Quote")

    @task
    def search_all(self):
        payload = {
            "show-all": "show-all",
            "show-all:search-all.x": "41",
            "show-all:search-all.y": "8",
            "javax.faces.ViewState": self.cor_viewState
        }
        with self.client.post("/InsuranceWebExtJS/agent_lookup.jsf",data=payload, cookies={"JSESSIONID": self.cor_jessionid,
                                                                            "UserSessionFilter.sessionId": self.cor_usersessionID},
                              name="T02_SearchAllAgents", catch_response=True) as response:
            if "Here is the list of all available Agents" in response.text:
                response.success()
                try:
                    cor_viewState = re.findall("j_id\d+:j_id\d+", response.text)
                    self.cor_viewState = cor_viewState[0]
                    # print("ViewStat is", self.cor_viewState)
                except AttributeError:
                    self.cor_viewState = ""
            else:
                response.failure("Text check not found>>Instant Auto Quote - Continued")
        raise StopUser

class MyLoadTest(HttpUser):
    host = "http://localhost:9090"
    tasks = [AgentLookup]
    wait_time = constant(1)
