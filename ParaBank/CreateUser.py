import datetime

from locust import SequentialTaskSet, User, HttpUser, task, events, constant
import json, re, os, sys
import logging

# building the path of the urls so as to make script platform independent

Root_Dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Application_folder = os.path.join(Root_Dir, "ParaBank")
CreatedUserFilePath = os.path.join(Application_folder, "CreatedUser.csv")

# CSV_File_location = os.path.join(Application_folder, "credentials_csv.csv")
# print("CSV File location is-",CSV_File_location)
logger = logging.getLogger(__name__)
sys.path.append(Root_Dir)


@events.spawning_complete.add_listener
def spawn_user(user_count):
    print("******************   {} Users have Ramped up".format(user_count))


@events.test_start.add_listener
def t_start(**kwargs):
    print("******************   The test has been STARTED at {}".format(datetime.datetime.now()))


@events.test_stop.add_listener
def t_stop(**kwargs):
    print("******************   The test has been STOPPED at {}".format(datetime.datetime.now()))


#           Main class to CREATE User


class CreateUser(SequentialTaskSet):

    def __init__(self, parent):
        super().__init__(parent)
        self.cor_jessionid = ""
        self.cor_CreatedUser = ""
        self.cor_usersessionID = ""
        self.MyUsername = ""
        self.MyPassword = ""

    def on_start(self):
        self.client.cookies.clear()

        # *********Launch Request*************************
        text_check = "Customer Login"
        with self.client.get("/index.htm", name="T01_Launch", catch_response=True) as response:
            if text_check in response.text:
                response.success()
            else:
                response.failure("Text Check not found")

        self.cor_jessionid = response.cookies["JSESSIONID"]

        # *********RegisterPage Request*************************

        with self.client.get("/register.htm", cookies={"JSESSIONID": self.cor_jessionid}, catch_response=True,
                             name="T02_registerUserPage") as response:
            response.success() if "Signing up is easy!" in response.text else response.failure()

    # ************************CreateUser Request

    @task
    def userCreate(self):
        for i in range(1,2):
            username = "Goodman" + str(i)
            payload = {
                "customer.firstName": "fname",
                "customer.lastName": "lname",
                "customer.address.street": "999 street",
                "customer.address.city": "city",
                "customer.address.state": "state",
                "customer.address.zipCode": "123456",
                "customer.phoneNumber": "9898989898",
                "customer.ssn": "11112222",
                "customer.username": username,
                "customer.password": "password",
                "repeatedPassword": "password"
            }
            text_check = "Your account was created successfully."
            with self.client.post("/register.htm", cookies={"JSESSIONID": self.cor_jessionid}, data=payload,
                                  catch_response=True, name="T03_CreateUser") as response:
                if text_check in response.text:
                    response.success()
                    try:
                        f = open(CreatedUserFilePath, 'a')
                        f.write("{}\n".format(username))
                        f.close()

                    except AttributeError:
                        logger.error("UserNotCreated")
                        return None

                else:
                    response.failure("{} UserNotCreatedSuccessfully".format(username))



class Run(HttpUser):
    host = "https://parabank.parasoft.com/parabank"
    wait_function = constant(10)
    tasks = [CreateUser]
