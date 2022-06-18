"""
hook into AA
"""

# Django
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

# AA SRP
from aasrp import __title__, urls
from aasrp.managers import AaSrpManager


class AaSrpMenuItem(MenuItemHook):  # pylint: disable=too-few-public-methods
    """
    This class ensures only authorized users will see the menu entry
    """

    def __init__(self):
        # Setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _(__title__),
            "far fa-money-bill-alt fa-fw",
            "aasrp:dashboard",
            navactive=["aasrp:"],
        )

    def render(self, request):
        """
        Check if the user has the permission to view this app
        :param request:
        :return:
        """

        if request.user.has_perm("aasrp.basic_access"):
            app_count = AaSrpManager.pending_requests_count_for_user(request.user)
            self.count = app_count if app_count and app_count > 0 else None

            return MenuItemHook.render(self, request)

        return ""


@hooks.register("menu_item_hook")
def register_menu():
    """
    Register our menu item
    :return:
    """

    return AaSrpMenuItem()


@hooks.register("url_hook")
def register_urls():
    """
    Register our basu url
    :return:
    """

    return UrlHook(urls, "aasrp", r"^ship-replacement/")
