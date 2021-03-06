import unittest
import dh_matcher
import requests
from multiprocessing import Process

server_address = 'http://127.0.0.1:5000'

element1 = {
    "image_url": "http://www.wga.hu/art/l/leonardo/04/0monalis.jpg",
    "webpage_url": "http://www.wga.hu/frames-e.html?/html/l/leonardo/04/1monali.html",
    "metadata": {
        "author": "LEONARDO da Vinci",
        "title": "Mona Lisa (La Gioconda)",
        "date": "1503-5",
        "WGA_id": 153647
    }
}


def _block_until_server_on():
    server_on = False
    while not server_on:
        try:
            requests.get(server_address, timeout=5)
            server_on = True
        except requests.ConnectionError:
            print('Waiting for server to be online...')
    print('Server is online!')


class TestDHMatcher(unittest.TestCase):

    def assert4xxError(self, response: requests.Response, msg: str):
        self.assertGreaterEqual(response.status_code, 400, msg)
        self.assertLess(response.status_code, 500, msg)

    def assert200Response(self, response: requests.Response, msg: str):
        self.assertEqual(response.status_code, 200, msg)

    def test_scenario2(self):
        # Adding element
        response = requests.post(server_address+'/database', json=element1)
        self.assert200Response(response, "Adding an element failed")

        # Search for that element
        search_parameters = {'positive_image_urls': [element1['image_url']]}
        response = requests.post(server_address+'/search', json=search_parameters)
        self.assert200Response(response, 'Basic search')
        search_parameters = {'positive_image_urls': [element1['image_url']+'fsjldk']}
        response = requests.post(server_address+'/search', json=search_parameters)
        self.assert4xxError(response, 'Trying with an image not in the database')

    def test_scenario1(self):
        # Adding element
        response = requests.post(server_address+'/database', json=element1)
        self.assert200Response(response, "Adding an element")
        response = requests.post(server_address+'/database', json={'image_url': 'http://sdjfhlqdkfjhlqsdkjfh.jpg'})
        self.assert4xxError(response, "Trying to add a wrong image")
        response = requests.post(server_address+'/database', json=element1)
        self.assert4xxError(response, "Trying to add an element that is already in the database")

        # Retrieving element
        response = requests.get(server_address+'/database/'+element1['image_url'])
        self.assert200Response(response, "Accessing an already added element")
        response = requests.get(server_address+'/database/truc')
        self.assert4xxError(response, "Trying to access an element that is not in the database")

        # Removing element
        response = requests.delete(server_address+'/database/truc')
        self.assert4xxError(response, "Trying to remove an non-existing element")
        response = requests.delete(server_address+'/database/'+element1['image_url'])
        self.assert200Response(response, "Removing an element")
        response = requests.get(server_address+'/database/'+element1['image_url'])
        self.assert4xxError(response, "Checking that element is not accessible anymore")
        response = requests.delete(server_address+'/database/'+element1['image_url'])
        self.assert4xxError(response, "Trying to remove an already removed element")

if __name__ == '__main__':
    # Initalisation
    server_process = Process(target=dh_matcher.app.run)
    server_process.start()
    _block_until_server_on()
    # Tests
    unittest.main()
    # Close server
    server_process.terminate()
    server_process.join()
