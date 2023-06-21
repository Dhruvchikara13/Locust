import random
import re

from locust import SequentialTaskSet, task, constant, HttpUser, between


class JPetStore(SequentialTaskSet):
    def __init__(self, parent):
        super().__init__(parent)
        self.jsessionid = ""
        self.cor_sourcePage = ""
        self.cor_fp = ""
        self.randCategory = ""
        self.randProduct = ""
        self.randItem = ""
        self.cor_OrderID = ""

    @task
    def enterStore(self):
        url = self.client.get("/actions/Catalog.action", catch_response=True, name="CreateUser_01_EnterStore")
        text_check = "JPetStore Demo"
        with url as response:
            response.success() if text_check in response.text else response.failure(
                "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))
        try:
            jsessionid = re.search("jsessionid=(.+?)\"", response.text)
            self.jsessionid = jsessionid.group(1)

            cor_sourcePage = re.search("name=\"_sourcePage\" value=\"(.+?)\" />", response.text)
            self.cor_sourcePage = cor_sourcePage.group(1)

            cor_fp = re.search("name=\"__fp\" value=\"(.+?)\" />", response.text)
            self.cor_fp = cor_fp.group(1)

            # print("JsessionId is {}".format(self.jsessionid))
            # print("SourcePage is {}".format(self.cor_sourcePage))
            # print("FP is {}".format(self.cor_fp))
        except AttributeError:
            self.jsessionid = ""
            self.cor_sourcePage = ""
            self.cor_fp = ""

    @task
    def createUser(self):
        for i in range(1, 101):
            prefix="jpet"
            firstname = prefix + str(i)
            lastname = prefix + str(i)
            email = firstname + "@test.com"
            payload = {
                "username": firstname,
                "password": "password",
                "repeatedPassword": "password",
                "account.firstName": firstname,
                "account.lastName": lastname,
                "account.email": email,
                "account.phone": "9898989898",
                "account.address1": "131",
                "account.address2": "131",
                "account.city": "noida",
                "account.state": "up",
                "account.zip": "123456",
                "account.country": "India",
                "account.languagePreference": "english",
                "account.favouriteCategoryId": "FISH",
                "account.listOption": "true",
                "account.bannerOption": "true",
                "newAccount": "Save Account Information",
                "_sourcePage": self.cor_sourcePage,
                "__fp": self.cor_fp
            }
            createdUrl = "/actions/Account.action"
            url = self.client.post(createdUrl, data=payload, catch_response=True, name="CreateUser_02_CreateUser")
            text_check = "Fish"
            with url as response:
                if text_check in response.text:
                    response.success()
                    f = open('C:\\Users\\dhruvchikara\\PycharmProjects\\LOCUST\\JPetStore\CreatedUser.csv', 'a')
                    f.write("{}\n".format(firstname))
                    f.close()

                else:
                    response.failure(
                        "Status code:{}>>Following text not found in response:{}".format(response.status_code,
                                                                                         text_check))




class LoadTest2(HttpUser):
    host = "https://petstore.octoperf.com/"
    tasks = [JPetStore]
    wait_time = between(2,5)
