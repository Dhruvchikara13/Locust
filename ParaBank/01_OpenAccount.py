import datetime
import random

from locust.exception import StopUser

# from ParaBank.csvreader import CSVReader
from locust import SequentialTaskSet, User, HttpUser, task, events, constant
import json, re, os, sys
import logging

# building the path of the urls so as to make script platform independent

Root_Dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Root-",Root_Dir)
Application_folder = os.path.join(Root_Dir, "ParaBank")
print("Application-",Application_folder)
CreatedUserFilePath = os.path.join(Application_folder, "CreatedUser.csv")
print("CSV-",CreatedUserFilePath)

# CSV_File_location = os.path.join(Application_folder, "credentials_csv.csv")
# print("CSV File location is-",CSV_File_location)
logger = logging.getLogger(__name__)
sys.path.append(Root_Dir)
from ParaBank.csvreader import CSVReader
my_reader = CSVReader(CreatedUserFilePath).read_data()




@events.spawning_complete.add_listener
def spawn_user(user_count):
    print("******************   {} Users have Ramped up".format(user_count))


@events.test_start.add_listener
def t_start(**kwargs):
    print("******************   The test has been STARTED at {}".format(datetime.datetime.now()))


@events.test_stop.add_listener
def t_stop(**kwargs):
    print("******************   The test has been STOPPED at {}".format(datetime.datetime.now()))


class OpenNewAccount(SequentialTaskSet):

    def __init__(self, parent):
        super().__init__(parent)
        self.cor_jessionid = ""
        self.cor_CreatedUser = ""
        self.cor_CustID = ""
        self.cor_ExistingAccounts = ""
        self.cor_CreatedAccount = ""
        self.cor_username=""

    def on_start(self):
        self.client.cookies.clear()

        # *********Launch Request*************************
        text_check = "Customer Login"
        with self.client.get("/index.htm", name="T01_Launch_OpenAccount", catch_response=True) as response:
            if text_check in response.text:
                response.success()
            else:
                response.failure("Text Check not found")

        self.cor_jessionid = response.cookies["JSESSIONID"]

        # ************************Login Request
        self.cor_username = random.choice(my_reader)['p_username']
        print(self.cor_username)
        payload = {
            "username": self.cor_username,
            "password": "password",
        }
        text_check = "ParaBank | Accounts Overview"
        with self.client.post("/login.htm", cookies={"JSESSIONID": self.cor_jessionid}, data=payload,
                              catch_response=True, name="T02_Login_OpenAccount") as response:
            if text_check in response.text:
                response.success()
                try:
                    cor_CustID = re.search("services_proxy/bank/customers/\" \+ (.+?) \+ \"/accounts", response.text)
                    self.cor_CustID = cor_CustID.group(1)
                    print("CustID is {}".format(self.cor_CustID))
                except AttributeError:
                    self.cor_CustID = ""

            else:
                response.failure("user failed")
                logger.error("User {} not able to login".format(payload['username']))
                raise StopUser

    @task
    def m1_OpenAccount(self):
        # ******************* CLick On Open Account Link
        text_check = "What type of Account would you like to open"
        with self.client.get("/openaccount.htm", name="T03_OpenAccountLink", catch_response=True) as response:
            if text_check in response.text:
                response.success()
            else:
                response.failure("{}:Text Check not found".format(text_check))

        # def get_account(self):
        url = "/services_proxy/bank/customers/" + self.cor_CustID + "/accounts"
        response = self.client.get(url, catch_response=True, cookies={"JSESSIONID": self.cor_jessionid})
        self.cor_ExistingAccounts = (re.search("'id': (.+?),", str(random.choices(response.json())))).group(1)

        # ******************* CreateAccount
        text_check = "id"
        url = "/services_proxy/bank/createAccount?customerId=" + self.cor_CustID + "&newAccountType=0&fromAccountId=" + self.cor_ExistingAccounts
        with self.client.post(url, cookies={"JSESSIONID": self.cor_jessionid}, name="T04_CreateAccount",
                              catch_response=True) as response:
            if text_check in response.text:
                response.success()
                self.cor_CreatedAccount = (re.search("'id': (.+?),", str(response.json()))).group(1)
                print(self.cor_CreatedAccount)
            else:
                response.failure("{}:Text Check not found".format(text_check))


class Run(HttpUser):
    host = "https://parabank.parasoft.com/parabank"
    wait_function = constant(1)
    tasks = [OpenNewAccount]
