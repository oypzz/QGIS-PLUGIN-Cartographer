# @Time  : 2024/5/22 11:13
# @Filename : test_heap.py
import heapq

# list = [0,4,42,6,8]
# # heapq.heapify(list)
#
# heapq.heappop(list)
# print(list)
# heapq.heappop(list)
# print(list)
class Person(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age


if __name__ == '__main__':
    a = (0, 8, 2, 6, 3)
    b = [('a', 12), ('b', 12), ('c', 1), ('d', 13), ('e', 2)]
    person_list = [Person('q', 2), Person('w', 1), Person('e', 3), Person('r', 6)]

    b.sort(key=lambda x: x[1])

    person_list.sort(key=lambda x: x.age)
    print(person_list)
    for i in person_list:
        print   (i.age)
