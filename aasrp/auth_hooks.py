"""
Hook into Alliance Auth to register menu items and URLs for the AA-SRP application.
This module defines hooks for integrating the AA-SRP module with the Alliance Auth framework.
"""

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

# AA SRP
from aasrp import __title_translated__, urls
from aasrp.models import SrpRequest


class AaSrpMenuItem(MenuItemHook):  # pylint: disable=too-few-public-methods
    """
    Custom menu item hook for the AA-SRP module.
    Ensures that only authorized users can see the menu entry in the sidebar.
    """

    def __init__(self) -> None:
        """
        Initialize the menu item with its text, icon, URL, and active navigation classes.
        """

        MenuItemHook.__init__(
            self,
            text=__title_translated__,
            classes="fa-regular fa-money-bill-1",
            url_name="aasrp:srp_links",
            navactive=["aasrp:"],
        )
        self.count = None

    def render(self, request) -> str:
        """
        Render the menu item if the user has the required permission.

        :param request: The HTTP request object.
        :type request: HttpRequest
        :return: The rendered menu item HTML or an empty string if the user lacks permission.
        :rtype: str
        """

        if not request.user.has_perm("aasrp.basic_access"):
            return ""

        # Get the count of pending SRP requests for the user
        app_count = SrpRequest.pending_requests_count_for_user(request.user)
        self.count = app_count if app_count and app_count > 0 else None

        return MenuItemHook.render(self, request=request)


@hooks.register("menu_item_hook")
def register_menu() -> AaSrpMenuItem:
    """
    Register the AA-SRP menu item with Alliance Auth.

    :return: The menu item hook instance.
    :rtype: AaSrpMenuItem
    """

    return AaSrpMenuItem()


@hooks.register("url_hook")
def register_urls() -> UrlHook:
    """
    Register the base URL for the AA-SRP module with Alliance Auth.

    :return: The URL hook instance.
    :rtype: UrlHook
    """

    return UrlHook(urls=urls, namespace="aasrp", base_url=r"^ship-replacement/")
