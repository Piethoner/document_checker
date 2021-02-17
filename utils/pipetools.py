from functools import partial


class PIPE:
    def __init__(self, func=None):
        self.func = func

    @classmethod
    def compose(cls, first, second):
        def composite(*args, **kwargs):
            return second(first(*args, **kwargs))
        return composite

    @classmethod
    def bind(cls, first, second):
        return cls(second if first is None else (first if second is None else cls.compose(first, second)))

    def __or__(self, next_func):
        return self.bind(self.func, next_func)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


pipe = PIPE()

if __name__ == '__main__':
    test = pipe|range|partial(filter, lambda x: x % 2)|list
    print(test(20))