# """
# Test auth_hooks
# """
#
# # Standard Library
# from http import HTTPStatus
#
# # Django
# from django.test import TestCase
# from django.urls import reverse
#
# # AA SRP
# from aasrp import __title__
# from aasrp.tests.utils import create_fake_user
#
#
# class TestHooks(TestCase):
#     """
#     Test the app hook into allianceauth
#     """
#
#     @classmethod
#     def setUpClass(cls) -> None:
#         """
#         Set up groups and users
#         """
#
#         super().setUpClass()
#
#         # User cannot access
#         cls.user_1001 = create_fake_user(
#             character_id=1001, character_name="Peter Parker"
#         )
#
#         # User can access
#         cls.user_1002 = create_fake_user(
#             character_id=1002,
#             character_name="Bruce Wayne",
#             permissions=["aasrp.basic_access"],
#         )
#
#         cls.html_menu = f"""
#             <li>
#                 <a class href="{reverse('aasrp:dashboard')}">
#                     <i class="far fa-money-bill-alt fa-fw"></i>
#                     {__title__}
#                 </a>
#             </li>
#         """
#
#     def test_render_hook_success(self):
#         """
#         Test should show the link to the app in the navigation to user with access
#
#         :return:
#         :rtype:
#         """
#
#         self.client.force_login(user=self.user_1002)
#
#         response = self.client.get(path=reverse(viewname="authentication:dashboard"))
#
#         self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
#         self.assertContains(response=response, text=self.html_menu, html=True)
#
#     def test_render_hook_fail(self):
#         """
#         Test should not show the link to the app in the
#         navigation to user without access
#
#         :return:
#         :rtype:
#         """
#
#         self.client.force_login(user=self.user_1001)
#
#         response = self.client.get(path=reverse(viewname="authentication:dashboard"))
#
#         self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
#         self.assertNotContains(response=response, text=self.html_menu, html=True)
