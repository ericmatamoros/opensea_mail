"""
Interfaces
"""
from opensea_mail.interfaces.Logger import Logger
from opensea_mail.interfaces.MailSender import MailSender
from opensea_mail.interfaces.OpenSeaCollector import OpenSeaCollector
from opensea_mail.interfaces.CoinMarketCapCollector import CoinMarketCapCollector

__all__: list[str] = [
    "CoinMarketCapCollector",
    "Logger",
    "MailSender",
    "OpenSeaCollector",
]
