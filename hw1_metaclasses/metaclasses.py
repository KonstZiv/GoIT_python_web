class Meta(type):

    children_number = 0

    def __new__(cls, clsname, bases, attrs):
        attrs['class_number'] = Meta.children_number
        Meta.children_number += 1
        return super(Meta, cls).__new__(cls, clsname, bases, attrs)


#Meta.children_number = 0

print('number of children classes: ', Meta.children_number)


class Cls1(metaclass=Meta):
    def __init__(self, data):
        self.data = data


class Cls2(metaclass=Meta):
    def __init__(self, data):
        self.data = data


print('Clas1 number: ', Cls1.class_number)

print('number of children classes: ', Meta.children_number)

print('Clas2 number: ', Cls2.class_number)
assert (Cls1.class_number, Cls2.class_number) == (0, 1)
a, b = Cls1(''), Cls2('')
assert (a.class_number, b.class_number) == (0, 1)
