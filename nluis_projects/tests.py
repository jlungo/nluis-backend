from django.test import TestCase
from django.urls import reverse, resolve


class UrlTest(TestCase):

    def testHomePage(self):
        response = self.client.get('/')
        print(response)

        self.assertEqual(response.status_code, 200)

    # def testCartPage(self):
    #     url = reverse('cart')
    #     print("Resolve : ", resolve(url))
    #
    #     self.assertEquals(resolve(url).func, cart)
