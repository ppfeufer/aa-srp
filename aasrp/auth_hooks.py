# coding=utf-8

"""
hook into AA
"""

from aasrp import urls, __title__
from aasrp.managers import AaSrpManager

from django.utils.translation import ugettext_lazy as _

from allianceauth.services.hooks import MenuItemHook, UrlHook
from allianceauth import hooks


class AaSrpMenuItem(MenuItemHook):  # pylint: disable=too-few-public-methods
    """
    This class ensures only authorized users will see the menu entry
    """

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _(__title__),
            "far fa-money-bill-alt fa-fw",
            "aasrp:dashboard",
            navactive=["aasrp:"],
        )

    def render(self, request):
        """
        check if the user has the permission to view this app
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
    register our menu item
    :return:
    """

    return AaSrpMenuItem()


@hooks.register("url_hook")
def register_urls():
    """
    register our basu url
    :return:
    """

    return UrlHook(urls, "aasrp", r"^ship-replacement/")
