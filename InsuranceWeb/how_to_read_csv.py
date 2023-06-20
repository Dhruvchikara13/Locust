from InsuranceWeb.csvreader import CSVReader
import random
my_reader=CSVReader("C:\\Users\\dhruvchikara\\PycharmProjects\\LOCUST\\InsuranceWeb\\credentials_csv.csv").read_data()

print(my_reader)


'''
# To get value sequentially. pop picks value from last to first
UserName=my_reader.pop()['username']
Password=my_reader.pop()['password']
print(UserName,Password)
'''

# To pick value randomly
UserName=random.choice(my_reader)['username']
Password=random.choice(my_reader)['password']
print(UserName,Password)