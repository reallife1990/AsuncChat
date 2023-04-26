class Message():
    __slots__ = ['a','b']

lst=[]

for i in range(5):
    o = Message()
    o.a=5+i
    o.b = 7+i
    lst.append(o)
    # del o


print(lst)
for obj in lst:
    print(obj.a, obj.b)