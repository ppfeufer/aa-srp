"""
providers
"""

from esi.clients import EsiClientProvider

from aasrp.constants import USERAGENT

esi = EsiClientProvider(app_info_text=USERAGENT)
