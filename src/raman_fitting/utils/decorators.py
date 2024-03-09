from typing import Callable
from functools import wraps, partial
from inspect import signature


def decorator_with_kwargs(decorator: Callable) -> Callable:
    """
    Source: https://gist.github.com/ramonrosa/402af55633e9b6c273882ac074760426
    Decorator factory to give decorated decorators the skill to receive
    optional keyword arguments.
    If a decorator "some_decorator" is decorated with this function:
        @decorator_with_kwargs
        def some_decorator(decorated_function, kwarg1=1, kwarg2=2):
            def wrapper(*decorated_function_args, **decorated_function_kwargs):
                '''Modifies the behavior of decorated_function according
                to the value of kwarg1 and kwarg2'''
                ...
            return wrapper
    It will be usable in the following ways:
        @some_decorator
        def func(x):
            ...
        @some_decorator()
        def func(x):
            ...
        @some_decorator(kwarg1=3)  # or other combinations of kwargs
        def func(x, y):
            ...
    :param decorator: decorator to be given optional kwargs-handling skills
    :type decorator: Callable
    :raises TypeError: if the decorator does not receive a single Callable or
        keyword arguments
    :raises TypeError: if the signature of the decorated decorator does not
        conform to: Callable, **keyword_arguments
    :return: modified decorator
    :rtype: Callable
    """

    @wraps(decorator)
    def decorator_wrapper(*args, **kwargs):
        if (len(kwargs) == 0) and (len(args) == 1) and callable(args[0]):
            return decorator(args[0])
        if len(args) == 0:
            return partial(decorator, **kwargs)
        raise TypeError(
            f"{decorator.__name__} expects either a single Callable "
            "or keyword arguments"
        )

    signature_values = signature(decorator).parameters.values()
    signature_args = [
        param.name for param in signature_values if param.default == param.empty
    ]

    if len(signature_args) != 1:
        raise TypeError(
            f"{decorator.__name__} signature should be of the form:\n"
            f"{decorator.__name__}(function: typing.Callable, "
            "kwarg_1=default_1, kwarg_2=default_2, ...) -> Callable"
        )

    return decorator_wrapper
