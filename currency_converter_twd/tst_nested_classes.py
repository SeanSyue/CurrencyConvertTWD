class Outer:
    class __Inner_1:
        def inner_func(self):
            print(f"inner_func of {self.__class__.__name__} is called")

        def _inner_func2(self):
            print(f"inner_func2 of {self.__class__.__name__} is called")

    class __Inner_2:
        def __init__(self):
            self.__a = 0

        @property
        def a(self):
            return self.__a

        @a.setter
        def a(self, value):
            self.__a = value

    class PublicInner:
        def _protected_inner_func(self):
            print(f"protected inner func of {self.__class__.__name__} is called")

        def __private_inner_func(self):
            print(f"private inner func of {self.__class__.__name__} is called")

    class _ProtectedInner:
        def _protected_inner_func(self):
            print(f"protected inner func of {self.__class__.__name__} is called")

        def __private_inner_func(self):
            print(f"private inner func of {self.__class__.__name__} is called")

    class __PrivateInner:
        def _protected_inner_func(self):
            print(f"protected inner func of {self.__class__.__name__} is called")

        def __private_inner_func(self):
            print(f"private inner func of {self.__class__.__name__} is called")

    def __init__(self):
        self.in_1 = self.__Inner_1()
        self.in_2 = self.__Inner_2()

    def call_inner_func(self):
        print(f"`call inner func` is called")
        self.in_1.inner_func()
        self.in_1._inner_func2()

    def set_value(self, value):
        self.in_2.a = value

    def print_value(self):
        print(f"value of a: {self.in_2.a}")


if __name__ == '__main__':
    ins = Outer()
    ins.call_inner_func()
    ins.set_value(1)
    ins.print_value()

    a = ins.PublicInner()
    a._protected_inner_func()
    # a.__private_inner_func()  # will fail]

    b = ins._ProtectedInner()
    b._protected_inner_func()
    # b.__private_inner_func()  # will fail

    # c = ins.__PrivateInner()  # will fail
    # c._protected_inner_func()  # will fail
    # c.__private_inner_func()  # will fail
