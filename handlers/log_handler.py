# File: handlers/log_handler.py

import logging
import re
from threading import Lock
from typing import List

class BufferLoggingHandler(logging.Handler):
    """
    Custom logging handler that appends log records to a shared buffer.
    Optionally sanitizes sensitive information like IP addresses.
    """
    # Regular expressions to identify IPv4 and IPv6 addresses
    IPV4_REGEX = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    IPV6_REGEX = re.compile(r'\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b')

    def __init__(self, buffer: List[str], buffer_lock: Lock, level=logging.DEBUG):
        """
        Initializes the BufferLoggingHandler.

        Args:
            buffer (List[str]): The shared buffer to append logs to.
            buffer_lock (Lock): A lock to ensure thread-safe operations.
            level (int): The logging level threshold.
        """
        super().__init__(level)
        self.buffer = buffer
        self.buffer_lock = buffer_lock

    def emit(self, record: logging.LogRecord):
        """
        Emits a log record after formatting and sanitizing it.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """
        try:
            msg = self.format(record)
            sanitized_msg = self.sanitize_ips(msg)
            with self.buffer_lock:
                self.buffer.append(sanitized_msg)
                if len(self.buffer) > 1000:
                    self.buffer.pop(0)  # Maintain buffer size
        except Exception:
            self.handleError(record)

    def sanitize_ips(self, message: str) -> str:
        """
        Sanitizes IP addresses in the log message.

        Args:
            message (str): The log message.

        Returns:
            str: The sanitized log message.
        """
        message = self.IPV4_REGEX.sub('[REDACTED IP]', message)
        message = self.IPV6_REGEX.sub('[REDACTED IP]', message)
        return message

class SanitizingHandler(logging.StreamHandler):
    """
    Custom logging handler that sanitizes sensitive information like IP addresses
    before outputting them to a stream (e.g., sys.stdout).
    """
    # Regular expressions to identify IPv4 and IPv6 addresses
    IPV4_REGEX = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    IPV6_REGEX = re.compile(r'\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b')

    def __init__(self, stream=None):
        """
        Initializes the SanitizingHandler.

        Args:
            stream (IO): The stream to output logs to (e.g., sys.stdout).
        """
        super().__init__(stream)

    def emit(self, record: logging.LogRecord):
        """
        Emits a log record after sanitizing IP addresses.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """
        try:
            msg = self.format(record)
            sanitized_msg = self.sanitize_ips(msg)
            self.stream.write(sanitized_msg + '\n')
            self.flush()
        except Exception:
            self.handleError(record)

    def sanitize_ips(self, message: str) -> str:
        """
        Sanitizes IP addresses in the log message.

        Args:
            message (str): The log message.

        Returns:
            str: The sanitized log message.
        """
        message = self.IPV4_REGEX.sub('[REDACTED IP]', message)
        message = self.IPV6_REGEX.sub('[REDACTED IP]', message)
        return message
