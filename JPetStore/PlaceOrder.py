import logging
import random
import re
import sys
import os
import locust_plugins
import datetime
from locust import events

from locust import SequentialTaskSet, task, constant, HttpUser, between

Root_Dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print("Root is-", Root_Dir)
Application_folder = os.path.join(Root_Dir, "JPetStore")
# print("Application is -", Application_folder)
CSV_File_location = os.path.join(Application_folder, "CreatedUser.csv")
# print("CSV is -", CSV_File_location)
Order_WriteLocation = os.path.join(Application_folder, "Order.csv")
# print("CSV File location is-",CSV_File_location)
sys.path.append(Root_Dir)

from FileCSVREAD import ClassCSVREAD


@events.spawning_complete.add_listener
def spawn_user(user_count):
    print("Spawing ......", user_count)


@events.test_start.add_listener
def t_start(**kwargs):
    print("The test has been STARTED at {}".format(datetime.datetime.now()))


@events.test_stop.add_listener
def t_stop(**kwargs):
    print("The test has been STOPPED at {}".format(datetime.datetime.now()))


class JPetFlow1(SequentialTaskSet):
    def __init__(self, parent):
        super().__init__(parent)
        self.test_data = ""
        self.jsessionid = ""
        self.cor_sourcePage = ""
        self.cor_fp = ""
        self.randCategory = ""
        self.randProduct = ""
        self.randItem = ""
        self.cor_OrderID = ""

    def on_start(self):
        url = self.client.get("/", catch_response=True, name="F1_T01_HomePage")
        text_check = "Welcome to JPetStore 6"
        with url as response:
            response.success() if text_check in response.text else response.failure(
                "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def enterStore(self):
        url = self.client.get("/actions/Catalog.action", catch_response=True, name="F1_T02_EnterStore")
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
    def signInPage(self):
        createdUrl = "/actions/Account.action;jsessionid=" + self.jsessionid + "?signonForm="
        url = self.client.get(createdUrl, catch_response=True, name="F1_T03_SignInPage")
        text_check = "Please enter your username and password"
        with url as response:
            response.success() if text_check in response.text else response.failure(
                "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def signIn(self):
        test_data = ClassCSVREAD(CSV_File_location).read()
        # print(test_data)
        logging.debug(test_data)
        self.test_data = test_data
        payload = {
            "username": test_data['name'],
            "password": "password",
            "signon": "Login",
            "_sourcePage": self.cor_sourcePage,
            "__fp": self.cor_fp
        }
        url = self.client.post("/actions/Account.action", data=payload, catch_response=True, name="F1_T04_SignIn")
        text_check = "Welcome " + test_data['name']
        with url as response:
            if text_check in response.text:
                response.success()
                try:
                    randCategory = re.findall("Catalog.action\?viewCategory=&categoryId=(.+?)\"", response.text)
                    self.randCategory = random.choice(randCategory)
                    # print("Random category is: {}".format(self.randCategory))
                except AttributeError:
                    self.randCategory = ""
            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def selectCategory(self):
        createdUrl = "/actions/Catalog.action?viewCategory=&categoryId=" + self.randCategory
        url = self.client.get(createdUrl, catch_response=True, name="F1_T05_SelectCategory")
        text_check = "Product ID"
        with url as response:
            if text_check in response.text:
                response.success()
                try:
                    randProduct = re.findall("/actions/Catalog.action\?viewProduct=&amp;productId=(.+?)\">",
                                             response.text)
                    self.randProduct = random.choice(randProduct)
                    # print("Random Product is: {}".format(self.randProduct))
                except AttributeError:
                    self.randProduct = ""
            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def selectProduct(self):
        createdUrl = "/actions/Catalog.action?viewProduct=&productId=" + self.randProduct
        url = self.client.get(createdUrl, catch_response=True, name="F1_T06_SelectProduct")
        text_check = "List Price"
        with url as response:
            if text_check in response.text:
                response.success()
                try:
                    randItem = re.findall("/actions/Catalog.action\?viewItem=&amp;itemId=(.+?)\">",
                                          response.text)
                    self.randItem = random.choice(randItem)
                    # print("Random Item is: {}".format(self.randItem))
                except AttributeError:
                    self.randItem = ""
            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def addToCart(self):
        createdUrl = "/actions/Cart.action?addItemToCart=&workingItemId=" + self.randItem
        url = self.client.get(createdUrl, catch_response=True, name="F1_T07_AddToCart")
        text_check = "Proceed to Checkout"
        with url as response:
            if text_check in response.text:
                response.success()
                # try:
                #     randItem = re.findall("/actions/Catalog.action\?viewItem=&amp;itemId=(.+?)\">",
                #                           response.text)
                #     self.randItem = random.choice(randItem)
                #     print("Random Item is: {}".format(self.randItem))
                # except AttributeError:
                #     self.randItem = ""
            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def ProceedToCheckout(self):
        createdUrl = "/actions/Order.action?newOrderForm="
        url = self.client.get(createdUrl, catch_response=True, name="F1_T08_ProceedToCheckout")
        text_check = "Payment Details"
        with url as response:
            if text_check in response.text:
                response.success()
                try:

                    cor_sourcePage = re.search("name=\"_sourcePage\" value=\"(.+?)\" />", response.text)
                    self.cor_sourcePage = cor_sourcePage.group(1)

                    cor_fp = re.search("name=\"__fp\" value=\"(.+?)\" />", response.text)
                    self.cor_fp = cor_fp.group(1)

                    # print("NewSourcePage is {}".format(self.cor_sourcePage))
                    # print("NewFP is {}".format(self.cor_fp))
                except AttributeError:

                    self.cor_sourcePage = ""
                    self.cor_fp = ""
            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def ProceedToPayment(self):
        payload = {
            "order.cardType": "Visa",
            "order.creditCard": "999 9999 9999 9999",
            "order.expiryDate": "12/03",
            "order.billToFirstName": "John",
            "order.billToLastName": "Dang",
            "order.billAddress1": "Sector 100",
            "order.billAddress2": "Sector 100",
            "order.billCity": "Noida",
            "order.billState": "UP",
            "order.billZip": "201201",
            "order.billCountry": "India",
            "newOrder": "Continue",
            "_sourcePage": self.cor_sourcePage,
            "__fp": self.cor_fp
        }
        createdUrl = "/actions/Order.action"
        url = self.client.post(createdUrl, data=payload, catch_response=True, name="F1_T09_ProceedToPayment")
        text_check = "Please confirm the information below and then"
        with url as response:
            if text_check in response.text:
                response.success()

            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def submitOrder(self):
        createdUrl = "/actions/Order.action?newOrder=&confirmed=true"
        url = self.client.get(createdUrl, catch_response=True, name="F1_T10_SubmitOrder")
        text_check = "Thank you, your order has been submitted"
        with url as response:
            if text_check in response.text:
                response.success()
                try:

                    cor_OrderID = re.search("Order #(.+?)\n", response.text)
                    self.cor_OrderID = cor_OrderID.group(1)
                    # print("OrderID is {}".format(self.cor_OrderID))
                    f = open(Order_WriteLocation, 'a')
                    f.write("{},{}\n".format(self.test_data['name'], self.cor_OrderID))
                    f.close()

                except AttributeError:

                    self.cor_OrderID = ""

            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def signOut(self):
        createdUrl = "/actions/Account.action?signoff="
        url = self.client.get(createdUrl, catch_response=True, name="F1_T11_SignOut")
        text_check = "Sign In"
        with url as response:
            response.success() if text_check in response.text else response.failure(
                "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))


class JPetFlow2(SequentialTaskSet):
    def __init__(self, parent):
        super().__init__(parent)
        self.test_data = ""
        self.jsessionid = ""
        self.cor_sourcePage = ""
        self.cor_fp = ""
        self.randCategory = ""
        self.randProduct = ""
        self.randItem = ""
        self.cor_OrderID = ""

    def on_start(self):
        url = self.client.get("/", catch_response=True, name="F2_T01_HomePage")
        text_check = "Welcome to JPetStore 6"
        with url as response:
            response.success() if text_check in response.text else response.failure(
                "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def enterStore(self):
        url = self.client.get("/actions/Catalog.action", catch_response=True, name="F2_T02_EnterStore")
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
    def signInPage(self):
        createdUrl = "/actions/Account.action;jsessionid=" + self.jsessionid + "?signonForm="
        url = self.client.get(createdUrl, catch_response=True, name="F2_T03_SignInPage")
        text_check = "Please enter your username and password"
        with url as response:
            response.success() if text_check in response.text else response.failure(
                "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def signIn(self):
        test_data = ClassCSVREAD(CSV_File_location).read()
        # print(test_data)
        logging.debug(test_data)
        self.test_data = test_data
        payload = {
            "username": test_data['name'],
            "password": "password",
            "signon": "Login",
            "_sourcePage": self.cor_sourcePage,
            "__fp": self.cor_fp
        }
        url = self.client.post("/actions/Account.action", data=payload, catch_response=True, name="F2_T04_SignIn")
        text_check = "Welcome " + test_data['name']
        with url as response:
            if text_check in response.text:
                response.success()
                try:
                    randCategory = re.findall("Catalog.action\?viewCategory=&categoryId=(.+?)\"", response.text)
                    self.randCategory = random.choice(randCategory)
                    # print("Random category is: {}".format(self.randCategory))
                except AttributeError:
                    self.randCategory = ""
            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def selectCategory(self):
        createdUrl = "/actions/Catalog.action?viewCategory=&categoryId=" + self.randCategory
        url = self.client.get(createdUrl, catch_response=True, name="F2_T05_SelectCategory")
        text_check = "Product ID"
        with url as response:
            if text_check in response.text:
                response.success()
                try:
                    randProduct = re.findall("/actions/Catalog.action\?viewProduct=&amp;productId=(.+?)\">",
                                             response.text)
                    self.randProduct = random.choice(randProduct)
                    # print("Random Product is: {}".format(self.randProduct))
                except AttributeError:
                    self.randProduct = ""
            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def selectProduct(self):
        createdUrl = "/actions/Catalog.action?viewProduct=&productId=" + self.randProduct
        url = self.client.get(createdUrl, catch_response=True, name="F2_T06_SelectProduct")
        text_check = "List Price"
        with url as response:
            if text_check in response.text:
                response.success()
                try:
                    randItem = re.findall("/actions/Catalog.action\?viewItem=&amp;itemId=(.+?)\">",
                                          response.text)
                    self.randItem = random.choice(randItem)
                    # print("Random Item is: {}".format(self.randItem))
                except AttributeError:
                    self.randItem = ""
            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def addToCart(self):
        createdUrl = "/actions/Cart.action?addItemToCart=&workingItemId=" + self.randItem
        url = self.client.get(createdUrl, catch_response=True, name="F2_T07_AddToCart")
        text_check = "Proceed to Checkout"
        with url as response:
            if text_check in response.text:
                response.success()
                # try:
                #     randItem = re.findall("/actions/Catalog.action\?viewItem=&amp;itemId=(.+?)\">",
                #                           response.text)
                #     self.randItem = random.choice(randItem)
                #     print("Random Item is: {}".format(self.randItem))
                # except AttributeError:
                #     self.randItem = ""
            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def ProceedToCheckout(self):
        createdUrl = "/actions/Order.action?newOrderForm="
        url = self.client.get(createdUrl, catch_response=True, name="F2_T08_ProceedToCheckout")
        text_check = "Payment Details"
        with url as response:
            if text_check in response.text:
                response.success()
                try:

                    cor_sourcePage = re.search("name=\"_sourcePage\" value=\"(.+?)\" />", response.text)
                    self.cor_sourcePage = cor_sourcePage.group(1)

                    cor_fp = re.search("name=\"__fp\" value=\"(.+?)\" />", response.text)
                    self.cor_fp = cor_fp.group(1)

                    # print("NewSourcePage is {}".format(self.cor_sourcePage))
                    # print("NewFP is {}".format(self.cor_fp))
                except AttributeError:

                    self.cor_sourcePage = ""
                    self.cor_fp = ""
            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def ProceedToPayment(self):
        payload = {
            "order.cardType": "Visa",
            "order.creditCard": "999 9999 9999 9999",
            "order.expiryDate": "12/03",
            "order.billToFirstName": "John",
            "order.billToLastName": "Dang",
            "order.billAddress1": "Sector 100",
            "order.billAddress2": "Sector 100",
            "order.billCity": "Noida",
            "order.billState": "UP",
            "order.billZip": "201201",
            "order.billCountry": "India",
            "newOrder": "Continue",
            "_sourcePage": self.cor_sourcePage,
            "__fp": self.cor_fp
        }
        createdUrl = "/actions/Order.action"
        url = self.client.post(createdUrl, data=payload, catch_response=True, name="F2_T09_ProceedToPayment")
        text_check = "Please confirm the information below and then"
        with url as response:
            if text_check in response.text:
                response.success()

            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def submitOrder(self):
        createdUrl = "/actions/Order.action?newOrder=&confirmed=true"
        url = self.client.get(createdUrl, catch_response=True, name="F2_T10_SubmitOrder")
        text_check = "Thank you, your order has been submitted"
        with url as response:
            if text_check in response.text:
                response.success()
                try:

                    cor_OrderID = re.search("Order #(.+?)\n", response.text)
                    self.cor_OrderID = cor_OrderID.group(1)
                    # print("OrderID is {}".format(self.cor_OrderID))
                    f = open(Order_WriteLocation, 'a')
                    f.write("{},{}\n".format(self.test_data['name'], self.cor_OrderID))
                    f.close()

                except AttributeError:

                    self.cor_OrderID = ""

            else:
                response.failure(
                    "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))

    @task
    def signOut(self):
        createdUrl = "/actions/Account.action?signoff="
        url = self.client.get(createdUrl, catch_response=True, name="F2_T11_SignOut")
        text_check = "Sign In"
        with url as response:
            response.success() if text_check in response.text else response.failure(
                "Status code:{}>>Following text not found in response:{}".format(response.status_code, text_check))


class LoadTest1(HttpUser):
    host = "https://petstore.octoperf.com/"
    tasks = [JPetFlow1]
    wait_time = constant(2)
    fixed_count = 5


class LoadTest2(HttpUser):
    host = "https://petstore.octoperf.com/"
    tasks = [JPetFlow2]
    wait_time = constant(2)
    fixed_count = 7

