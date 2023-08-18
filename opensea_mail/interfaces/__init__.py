"""
Interfaces
"""
from opensea_mail.interfaces.Logger import Logger
from opensea_mail.interfaces.MailSender import MailSender
from opensea_mail.interfaces.OpenSeaCollector import OpenSeaCollector

__all__: list[str] = [
    "Logger",
    "MailSender",
    "OpenSeaCollector",
]
