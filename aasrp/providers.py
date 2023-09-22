"""
Providers
"""

# Alliance Auth
from esi.clients import EsiClientProvider

# AA SRP
from aasrp.constants import USERAGENT

# ESI client
esi = EsiClientProvider(app_info_text=USERAGENT)
