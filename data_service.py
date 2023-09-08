import re
numbers = [2, 3, 5, 2, 11, 2, 7]

# check the count of 2
count = numbers.count(1)


print('Count of 2:', count)
data = "Average (111 and 1111 and 222 and 22222 and 2333 shop id)"
m = re.findall(r"\(.*shop id\)", data)
if len(m) > 0 and "Average" in data:
    tmp_str = m[0].replace("(", "")
    tmp_str = tmp_str.replace(")", "")
    tmp_str = tmp_str.replace("shop id", "")
    tmp_str = tmp_str.replace("and", "")
    tmp_str = re.sub(r"\s+", " ", tmp_str)
    tmp_str = tmp_str.split(" ")
    tmp_str = [x for x in tmp_str if x]
    print(tmp_str)
    if len(tmp_str) >= 5:
        print('k')
