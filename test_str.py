
import re

# initializing string
test_string = "channel1"

# printing original string
print("The original string : " + test_string)

# getting numbers from string
temp = re.findall(r'\d+', test_string)
res = list(map(int, temp))

# print result
print("The numbers list is : " + str(res[0]))