import unittest
from fastapi.testclient import TestClient
import json

from main import app

client = TestClient(app)
TEST_DATA_PATH = './test_data.json'


def read_test_data(path):
    with open(path) as f:
        data = json.load(f)
    return data


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.data = read_test_data(TEST_DATA_PATH)
        for i in range(0, len(self.data)):
            response = client.post("/measurement_values/", json=self.data[i]).json()
            self.data[i]['id'] = response['id']

    def tearDown(self):
        response = client.get("/measurement_values/")
        for data in response.json():
            client.delete("/measurement_values/" + str(data['id']))

    def test_read_value(self):
        response = client.get("/measurement_values/" + str(self.data[0]['id']))
        self.assertEqual(response.status_code, 200, 'Wrong status code')
        self.assertDictEqual(response.json(), self.data[0], 'Got the wrong object')

    def test_read_inexistent_value(self):
        response = client.get("/measurement_values/0")
        assert response.status_code == 404

    def test_create_and_delete_value(self):
        # test post
        obj = self.data[0].copy()
        del obj['id']
        response = client.post("/measurement_values/", json=obj)
        self.assertEqual(response.status_code, 200, 'Wrong post status code')
        new_id = response.json()['id']
        response = client.get("/measurement_values/" + str(new_id))
        new_obj = response.json()
        self.assertEqual(new_id, new_obj.pop('id'))
        self.assertDictEqual(obj, new_obj, 'Got a different object by this id')

        # test delete
        response = client.delete("/measurement_values/" + str(new_id))
        self.assertEqual(response.status_code, 200, 'Wrong delete status code')
        response = client.get("/measurement_values/" + str(new_id))
        self.assertEqual(response.status_code, 404, "Record hasn't been deleted")

    def test_get_aggregations(self):
        test_params = {'type': 'degrees', 'sensor_id': 100}
        url = f"http://127.0.0.1:8000/aggregations/"
        url += f"?agg_time=hour&type={test_params['type']}&sensor_id={test_params['sensor_id']}"
        response = client.get(url)
        self.assertEqual(response.status_code, 200, 'Wrong status code')
        data = response.json()[0]

        # check if filtering work well
        self.assertEqual(data['type'], test_params['type'])
        self.assertEqual(data['sensor_id'], test_params['sensor_id'])

        # check statistics (see test case data in test_data.json)
        self.assertEqual(data['mean'], 720)
        self.assertEqual(data['min'], 700)
        self.assertEqual(data['max'], 740)


if __name__ == '__main__':
    unittest.main()
