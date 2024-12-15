"""
Providers
"""

# Alliance Auth
from esi.clients import EsiClientProvider

# AA SRP
from aasrp.constants import USER_AGENT_ESI

# ESI client
esi = EsiClientProvider(app_info_text=USER_AGENT_ESI)
