def arbitrary_args_test(name_, *args, condition=True):
    print(f"{name_ = }")
    if condition:
        print(f"{condition = }")
        if args:
            for n in args:
                print(f"{n = }")


if __name__ == '__main__':
    arbitrary_args_test(1)
    arbitrary_args_test(1, 2, 3)
    arbitrary_args_test(1, condition=False)
