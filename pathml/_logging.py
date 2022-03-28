"""
Copyright 2021, Dana-Farber Cancer Institute and Weill Cornell Medicine
License: GNU GPL 2.0
"""

from loguru import logger
import functools
import sys


class PathMLLogger:

    logger.disable("pathml")
    logger.disable(__name__)

    @staticmethod
    def toggle_logging(
        enabled=True,
        sink=sys.stderr,
        level="DEBUG",
        fmt="{time:HH:mm:ss} | {level:<8} | {module} | {function: ^15} | {line: >3} | {message}",
        **kwargs
    ):
        """
        Convenience method for turning on or off logging for PathML.
        Note that this can also be achieved by interfacing with loguru directly

        Args:
            enabled (bool):
                Whether to save logs. Defaults to ``True``.
            sink (str or io._io.TextIOWrapper, optional):
                Destination sink for log messages. Defaults to ``sys.stderr``.
            level (str):
                level of logs to capture. Defaults to 'DEBUG'.
            fmt (str):
                Formatting for the log message. Defaults to: '{time:HH:mm:ss} | {level:<8} | {module} | {function: ^15} | {line: >3} | {message}'
            **kwargs (dict, optional):
                additional options passed to configure logger. See:
                `loguru documentation <https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add>`_

        Example::

            from pathml import PathMLLogger

            # turn on logging for PathML
            PathMLLogger.toggle_logging(enabled=True)

            # turn off logging for PathML
            PathMLLogger.toggle_logging(enabled=False)

            # turn on logging and output logs to a file named 'logs.txt' in home directory, with colorization enabled
            PathMLLogger.toggle_logging(enabled=True, sink="~/logs.txt", colorize=True)

        """
        handler_id = None
        if enabled:
            logger.enable("pathml")
            logger.enable(__name__)
            handler_id = logger.add(sink=sink, level=level, format=fmt, **kwargs)
            logger.info("Enabled Logging For PathML!")
            return handler_id

        else:
            logger.disable("pathml")
            logger.disable(__name__)
            logger.info(
                "Disabled Logging For PathML! If you are seeing this, there is a problem"
            )

        logger.info("If you are seeing this, there is a problem")
        return handler_id


# courtesy of the people at loguru
# https://loguru.readthedocs.io/en/stable/resources/recipes.html#:~:text=or%20fallback%20policy.-,Logging%20entry%20and%20exit%20of%20functions%20with%20a%20decorator,-%EF%83%81
def logger_wraps(*, entry=True, exit=True, level="DEBUG"):
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.bind(enter_exit=True).log(
                    level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs
                )
            result = func(*args, **kwargs)
            if exit:
                logger_.bind(enter_exit=True).log(
                    level, "Exiting '{}' (result={})", name, result
                )
            return result

        return wrapped

    return wrapper
