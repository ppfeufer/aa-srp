"""
Hook into AA
"""

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

# AA SRP
from aasrp import __title__, urls
from aasrp.models import SrpRequest


class AaSrpMenuItem(MenuItemHook):  # pylint: disable=too-few-public-methods
    """
    This class ensures only authorized users will see the menu entry
    """

    def __init__(self):
        # Setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            text=__title__,
            classes="fa-regular fa-money-bill-1",
            url_name="aasrp:srp_links",
            navactive=["aasrp:"],
        )
        self.count = None

    def render(self, request):
        """
        Check if the user has the permission to view this app

        :param request:
        :type request:
        :return:
        :rtype:
        """

        if request.user.has_perm("aasrp.basic_access"):
            app_count = SrpRequest.objects.pending_requests_count_for_user(request.user)
            self.count = app_count if app_count and app_count > 0 else None

            return MenuItemHook.render(self, request=request)

        return ""


@hooks.register("menu_item_hook")
def register_menu():
    """
    Register our menu item

    :return:
    :rtype:
    """

    return AaSrpMenuItem()


@hooks.register("url_hook")
def register_urls():
    """
    Register our base url

    :return:
    :rtype:
    """

    return UrlHook(urls=urls, namespace="aasrp", base_url=r"^ship-replacement/")
