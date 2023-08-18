# -*- coding: utf-8 -*-
"""
Logger classes.
"""
import logging

from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class DefaultLogger(logging.Logger):
    """
    Default logger.

    It includes 3 handlers by default:

    * A stream handler
    * A rotating file handler
    * A timed rotating file handler

    The stream handler outputs traces to sys.stdout and sys.stderr (i.e. the console).

    The rotating file handler saves traces in files. Files have a maximum size in bytes.
    When the size is nearly the maximum length, rollover occurs.

    The timed rotating file handler also saves traces in files. In this case, rollover
    happens at certain timed intervals.

    All of them can be activated and deactivated. However, only the stream handler is
    activated by default.

    There should be one unique logger, and it should be created in the top-level package
    (in Stock Movement Forecasting/__init__.py).
    """
    _base_style = "%(asctime)s - %(name)s - %(levelname)s - %(threadName)s"
    _c_style = _base_style + " - %(message)s"
    _f_style = _base_style + " - %(module)s - %(funcName)s - %(message)s"

    def __init__(self, name):
        # Formatter
        super().__init__(name)

        # Console handler
        self._c_handler = None

        # Rotating file handler
        self._rf_handler = None

        # Timed rotating file handler
        self._tf_handler = None

    def set_console_logs(self, level):
        """
        Activate console (stream) handler.

        :param level: Logging level.
        """
        # Remove old handler
        self.unset_console_logs()

        # New handler
        self._c_handler = logging.StreamHandler()
        self._c_handler.setLevel(level)
        self._c_handler.setFormatter(logging.Formatter(DefaultLogger._c_style))

        # Add handler to logger
        self.addHandler(self._c_handler)

    def unset_console_logs(self):
        """
        Deactivate console handler.
        """
        # Remove old handler
        if self._c_handler:
            self.removeHandler(self._c_handler)

        self._c_handler = None

    def set_rotating_logs(self,
                          level,
                          filename,
                          max_bytes=5000000,
                          backup_count=5):
        """
        Activate a logging rotating file handler (to save traces in files).

        Rollover will occur whenever the current log file is nearly max_bytes in length.

        If max_bytes is zero, rollover never occurs.

        :param level: Logging level
        :param filename: The name for the log file
        :param max_bytes: Log file max size in bytes, defaults to 5000000
        :param backupcount: Max number of files to be kept, defaults to 5
        """
        self.unset_rotating_logs()

        # New handler
        self._rf_handler = RotatingFileHandler(filename,
                                               maxBytes=max_bytes,
                                               backupCount=backup_count)
        self._rf_handler.setLevel(level)
        self._rf_handler.setFormatter(logging.Formatter(DefaultLogger._f_style))

        # Add handler to logger
        self.addHandler(self._rf_handler)

    def unset_rotating_logs(self):
        """
        Deactivate rotating file logs handler.
        """
        if self._rf_handler:
            self.removeHandler(self._rf_handler)

        self._rf_handler = None

    def set_timed_rotating_logs(self,
                                level,
                                filename,
                                when="D",
                                interval=1,
                                backup_count=7):
        """
        Activate a logging timed rotating file handler (to save traces in files).

        Rollover will occur at certain timed intervals, which are defined by when and interval.

        If backup_count is nonzero, at most backup_count files will be kept, and if more
        would be created when rollover occurs, the oldest one is deleted.

        The deletion logic uses the interval to determine which files to delete, so changing
        the interval may leave old files lying around.

        :param level: Logging level
        :param filename: The name for the log file, defaults to "logs/app.log"
        :param when: Type of interval, defaults to "D"
        :param interval: Number of intervals, defaults to 1
        :param backup_count: Max number of files to be kept, defaults to 7
        """
        self.unset_timed_rotating_logs()

        # New handler
        self._tf_handler = TimedRotatingFileHandler(filename,
                                                    when=when,
                                                    interval=interval,
                                                    backupCount=backup_count)
        self._tf_handler.setLevel(level)
        self._tf_handler.setFormatter(logging.Formatter(DefaultLogger._f_style))

        # Add handler to logger
        self.addHandler(self._tf_handler)

    def unset_timed_rotating_logs(self):
        """
        Deactivate timed rotating file logs handler.
        """
        if self._tf_handler:
            self.removeHandler(self._tf_handler)

        self._tf_handler = None

    def close(self):
        """
        Close handlers.
        """
        self._rf_handler.close()
        self._tf_handler.close()


def create_logger(name):
    """
    Get a logger and configure it if needed. Logger's class is DefaultLogger.

    Multiple calls to create_logger() with the same name will always return a reference to
    the same Logger object.

    :param name: Logger reference name.
    """
    logging.setLoggerClass(DefaultLogger)

    logger = logging.getLogger(name)

    logger.setLevel(logging.DEBUG)
    logger.set_console_logs(logging.DEBUG)

    logger.propagate = False

    return logger
