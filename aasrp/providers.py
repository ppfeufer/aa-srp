"""
Providers
"""

# Alliance Auth
from esi.clients import EsiClientProvider

# AA SRP
from aasrp import __app_name_useragent__, __github_url__, __version__

# ESI client
esi = EsiClientProvider(
    ua_appname=__app_name_useragent__, ua_version=__version__, ua_url=__github_url__
)
