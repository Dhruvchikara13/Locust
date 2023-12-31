import datetime,time
import math

from locust import SequentialTaskSet, HttpUser, task, constant, events, TaskSet, User, LoadTestShape
import re
from InsuranceWeb.csvreader import CSVReader
import random
import os
import logging
from locust.exception import StopUser
import sys
import locust_plugins

Root_Dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print("Root path is-", Root_Dir)
Application_folder = os.path.join(Root_Dir, "InsuranceWeb")
# print("Application Folder is-",Application_folder)
CSV_File_location = os.path.join(Application_folder, "credentials_csv.csv")
# print("CSV File location is-",CSV_File_location)
logger = logging.getLogger(__name__)
sys.path.append(Root_Dir)
my_reader = CSVReader(CSV_File_location).read_data()


@events.spawning_complete.add_listener
def spawn_user(user_count):
    print("***All Users ahve Ramped up", user_count)


@events.test_start.add_listener
def t_start(**kwargs):
    print("***The test has been STARTED at {}".format(datetime.datetime.now()))


@events.test_stop.add_listener
def t_stop(**kwargs):
    print("***The test has been STOPPED at {}".format(datetime.datetime.now()))


class MainClass(TaskSet):

    def __init__(self, parent):
        super().__init__(parent)
        self.cor_jessionid = ""
        self.cor_viewState = ""
        self.cor_usersessionID = ""
        self.MyUsername = ""
        self.MyPassword = ""

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
                self.parent.environment.runner.quit()
        self.cor_jessionid = response.cookies["JSESSIONID"]
        self.MyUsername = random.choice(my_reader)['username']
        self.MyPassword = random.choice(my_reader)['password']
        # print(self.MyUsername,self.MyPassword)
        payload = {
            "login-form": "login-form",
            "login-form:email": self.MyUsername,
            "login-form:password": self.MyPassword,
            "login-form:login.x": "43",
            "login-form:login.y": "10",
            "javax.faces.ViewState": self.cor_viewState
        }
        with self.client.post("/InsuranceWebExtJS/index.jsf", data=payload,
                              cookies={"JSESSIONID": self.cor_jessionid},
                              name="Login", catch_response=True) as response:
            if "Logged in as" in response.text:
                response.success()
                # logger.error("Login successful for user-" + self.MyUsername)
            else:
                response.failure("Login failed")
                logger.critical("User failed to login-" + self.MyUsername)
                # raise StopUser

        self.cor_usersessionID = response.cookies["UserSessionFilter.sessionId"]
        # print("UserSessionid is",self.cor_usersessionID)

    @task
    class AutoQuote(SequentialTaskSet):
        # wait_time=constant(10)

        @task
        def auto_quote(self):
            with self.client.get("/InsuranceWebExtJS/quote_auto.jsf", cookies={"JSESSIONID": self.parent.cor_jessionid,
                                                                               "UserSessionFilter.sessionId": self.parent.cor_usersessionID},
                                 name="AutoQuote_T01_AutoQuotePage", catch_response=True) as response:
                if "Automobile Instant Quote" in response.text:
                    response.success()
                    try:
                        cor_viewState = re.findall("j_id\d+:j_id\d+", response.text)
                        self.parent.cor_viewState = cor_viewState[0]
                        # print("ViewStat is", self.cor_viewState)
                    except AttributeError:
                        self.parent.cor_viewState = ""
                else:
                    response.failure("Text check not found>>Automobile Instant Quote")

        @task
        def getinstantautoquote(self):
            payload = {
                "autoquote": "autoquote",
                "autoquote:zipcode": "123456",
                "autoquote:e-mail": "john@test.com",
                "autoquote:vehicle": "car",
                "autoquote:next.x": "40",
                "autoquote:next.y": "8",
                "javax.faces.ViewState": self.parent.cor_viewState
            }
            with self.client.post("/InsuranceWebExtJS/quote_auto.jsf", data=payload,
                                  cookies={"JSESSIONID": self.parent.cor_jessionid,
                                           "UserSessionFilter.sessionId": self.parent.cor_usersessionID},
                                  name="AutoQuote_T02_InstantQuotePage-1", catch_response=True) as response:
                if "Instant Auto Quote - Continued" in response.text:
                    response.success()
                    try:
                        cor_viewState = re.findall("j_id\d+:j_id\d+", response.text)
                        self.parent.cor_viewState = cor_viewState[0]
                        # print("ViewStat is", self.cor_viewState)
                    except AttributeError:
                        self.parent.cor_viewState = ""
                else:
                    response.failure("Text check not found>>Instant Auto Quote - Continued")

        @task
        def getinstantautoquote_cont(self):
            payload = {
                "autoquote": "autoquote",
                "autoquote:age": "30",
                "autoquote:gender": "Male",
                "autoquote:type": "Excellent",
                "autoquote:next.x": "40",
                "autoquote:next.y": "8",
                "javax.faces.ViewState": self.parent.cor_viewState
            }
            with self.client.post("/InsuranceWebExtJS/quote_auto2.jsf", data=payload,
                                  cookies={"JSESSIONID": self.parent.cor_jessionid,
                                           "UserSessionFilter.sessionId": self.parent.cor_usersessionID},
                                  name="AutoQuote_T03_InstantQuotePage-2", catch_response=True) as response:
                if "Financial Info" in response.text:
                    response.success()
                    try:
                        cor_viewState = re.findall("j_id\d+:j_id\d+", response.text)
                        self.parent.cor_viewState = cor_viewState[0]
                        # print("ViewStat is", self.cor_viewState)
                    except AttributeError:
                        self.parent.cor_viewState = ""
                else:
                    response.failure("Text check not found>>Financial Info")

        @task
        def getinstantautoquote_cont2(self):
            payload = {
                "autoquote": "autoquote",
                "autoquote:year": "2022",
                "makeCombo": "Toyota",
                "autoquote:make": "Toyota",
                "modelCombo": "Camry",
                "autoquote:model": "Camry",
                "autoquote:finInfo": "Own",
                "autoquote:next.x": "37",
                "autoquote:next.y": "3",
                "javax.faces.ViewState": self.parent.cor_viewState
            }
            with self.client.post("/InsuranceWebExtJS/quote_auto3.jsf", data=payload,
                                  cookies={"JSESSIONID": self.parent.cor_jessionid,
                                           "UserSessionFilter.sessionId": self.parent.cor_usersessionID},
                                  name="AutoQuote_T04_InstantQuotePage-3", catch_response=True) as response:
                if "Your Instant Quote is" in response.text:
                    response.success()
                    try:
                        cor_viewState = re.findall("j_id\d+:j_id\d+", response.text)
                        self.parent.cor_viewState = cor_viewState[0]
                        # print("ViewStat is", self.cor_viewState)
                    except AttributeError:
                        self.parent.cor_viewState = ""
                else:
                    response.failure("Text check not found>>Your Instant Quote is")

        @task
        def purchase_a_quote_page(self):
            payload = {
                "quote-result": "quote-result",
                "quote-result:purchase-quote.x": "44",
                "quote-result:purchase-quote.y": "12",
                "javax.faces.ViewState": self.parent.cor_viewState
            }
            with self.client.post("/InsuranceWebExtJS/quote_result.jsf", data=payload,
                                  cookies={"JSESSIONID": self.parent.cor_jessionid,
                                           "UserSessionFilter.sessionId": self.parent.cor_usersessionID},
                                  name="AutoQuote_T05_PurchasePage", catch_response=True) as response:
                if "Purchase A Quote" in response.text:
                    response.success()
                    try:
                        cor_viewState = re.findall("j_id\d+:j_id\d+", response.text)
                        self.parent.cor_viewState = cor_viewState[0]
                        # print("ViewStat is", self.cor_viewState)
                    except AttributeError:
                        self.parent.cor_viewState = ""
                else:
                    response.failure("Text check not found>>Purchase A Quote")

        @task
        def final_purchase(self):
            payload = {
                "purchaseQuote": "purchaseQuote",
                "purchaseQuote:cardname": "John kumar",
                "purchaseQuote:cardnumber": "1294 4863 2356 3975",
                "purchaseQuote:expiration": "02/09",
                "purchaseQuote:purchase.x": "50",
                "purchaseQuote:purchase.y": "10",
                "javax.faces.ViewState": self.parent.cor_viewState
            }
            with self.client.post("/InsuranceWebExtJS/quote_result.jsf", data=payload,
                                  cookies={"JSESSIONID": self.parent.cor_jessionid,
                                           "UserSessionFilter.sessionId": self.parent.cor_usersessionID},
                                  name="AutoQuote_T06_FinalPurchase", catch_response=True) as response:
                if "Congratulations" in response.text:
                    response.success()


                else:
                    response.failure("Text check not found>>Congratulations")

        # @task
        # def stop(self):
        #     self.interrupt()

    @task
    class AgentLookup(SequentialTaskSet):
        # wait_time = constant(5)

        @task
        def agent_lookup(self):
            with self.client.get("/InsuranceWebExtJS/agent_lookup.jsf",
                                 cookies={"JSESSIONID": self.parent.cor_jessionid,
                                          "UserSessionFilter.sessionId": self.parent.cor_usersessionID},
                                 name="Agentlookup_T01_AgentLookupTab", catch_response=True) as response:
                if "Get in touch with an Insurance Co. agent" in response.text:
                    response.success()
                    try:
                        cor_viewState = re.findall("j_id\d+:j_id\d+", response.text)
                        self.parent.cor_viewState = cor_viewState[0]
                        # print("ViewStat is", self.cor_viewState)
                    except AttributeError:
                        self.parent.cor_viewState = ""
                else:
                    response.failure("Text check not found>>Automobile Instant Quote")

        @task
        def search_all(self):
            payload = {
                "show-all": "show-all",
                "show-all:search-all.x": "41",
                "show-all:search-all.y": "8",
                "javax.faces.ViewState": self.parent.cor_viewState
            }
            with self.client.post("/InsuranceWebExtJS/agent_lookup.jsf", data=payload,
                                  cookies={"JSESSIONID": self.parent.cor_jessionid,
                                           "UserSessionFilter.sessionId": self.parent.cor_usersessionID},
                                  name="Agentlookup_T02_SearchAllAgents", catch_response=True) as response:
                if "Here is the list of all available Agents" in response.text:
                    response.success()
                    try:
                        cor_viewState = re.findall("j_id\d+:j_id\d+", response.text)
                        self.parent.cor_viewState = cor_viewState[0]
                        # print("ViewStat is", self.cor_viewState)
                    except AttributeError:
                        self.parent.cor_viewState = ""
                else:
                    response.failure("Text check not found>>Instant Auto Quote - Continued")
            time.sleep(10)

        # @task
        # def stop(self):
        #     self.interrupt()


class MyLoadTest(HttpUser):
    host = "http://localhost:9090"
    tasks = {MainClass.AutoQuote:5,MainClass.AgentLookup:2}
    wait_time = constant(0.001)


# class StagesShape(LoadTestShape):
#
#
#     stages = [
#         {"duration": 20, "users": 30, "spawn_rate": 3},
#         {"duration": 40, "users": 30, "spawn_rate": 1},
#         {"duration": 60, "users": 0, "spawn_rate": 5},
#
#     ]
#
#     def tick(self):
#         run_time = self.get_run_time()
#
#         for stage in self.stages:
#             if run_time < stage["duration"]:
#                 tick_data = (stage["users"], stage["spawn_rate"])
#                 return tick_data
#
#
#         return None

#