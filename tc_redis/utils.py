# -*- coding: utf-8 -*-


class on_exception(object):  # NOQA

    def __init__(self, callback, exception_class=Exception):
        self.callback = callback
        self.exception_class = exception_class

    def __call__(self, fn):
        def wrapper(*args, **kwargs):
            self_instance = args[0] if len(args) > 0 else None
            try:
                return fn(*args, **kwargs)
            except self.exception_class as exc_value:
                if self.callback:
                    # Execute the callback and let it handle the exception
                    if self_instance:
                        return self.callback(
                            self_instance,
                            fn.__name__,
                            self.exception_class,
                            exc_value
                        )
                    else:
                        return self.callback(
                            fn.__name__,
                            self.exception_class,
                            exc_value
                        )
                else:
                    raise

        return wrapper
