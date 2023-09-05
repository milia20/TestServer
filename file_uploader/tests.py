import os

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from parameterized import parameterized

from file_uploader.models import UploadFile, User


class UploaderTests(APITestCase):

    @classmethod
    def setUp(cls):
        u = User.objects.create_user('test_user', password='test', email='test@mail.ru')
        u.save()
        t = Token.objects.create(user=u)
        t.save()
        UploadFile.objects.create(owner=u, file=os.path.basename(open(r'.\media\covid_worldwide.csv').name)).save()
        UploadFile.objects.create(owner=u, file=os.path.basename(open(r'.\media\Survey_AI.csv').name)).save()

    def test_unauthorized_upload(self):
        url = reverse('upload')
        client = APIClient()
        f = open(r'..\test_datasets\prc_hpi_a__custom_3617733_page_linear.csv')
        data = {'datafile': f}
        response = client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(UploadFile.objects.count(), 2)

    def test_authorized_upload(self):
        url = reverse('upload')
        f = open(r'..\test_datasets\prc_hpi_a__custom_3617733_page_linear.csv')
        data = {'datafile': f}
        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UploadFile.objects.count(), 3)
        self.assertEqual(response.data.get('owner'), 1)
        self.assertTrue(response.data.get('created'))
        self.assertTrue(response.data.get('file'))

    def test_get_files_list(self):
        url = reverse('upload')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(response.data[0].get('owner'))
        self.assertTrue(response.data[0].get('created'))
        self.assertTrue(response.data[0].get('file'))
        self.assertTrue(response.data[0].get('fields'))

    @parameterized.expand([
        ('', status.HTTP_404_NOT_FOUND),
        ('/drop', status.HTTP_404_NOT_FOUND),
        ('/drop/Survey_AI.csv/', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?filter=Q12.Gender', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?filter=XXX', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?filter=Q12.Gender&filter=Q15.Passed_exams', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?sort=Q12.Gender', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?sort=Q12.Gender&sort=Q15.Passed_exams', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?sort=XXX', status.HTTP_400_BAD_REQUEST),
        ('/drop/Survey_AI.csv/?sort=Q12.Gender&sort=XXX', status.HTTP_400_BAD_REQUEST),
        ('/drop/Survey_AI.csv/?sort=Q12.Gender&ascending=True', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?sort=Q12.Gender&ascending=True&ascending=True', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?filter=Q15.Passed_exams&Q12.Gender', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?ascending=True', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?sort=Q12.Gender&sort=Q15.Passed_exams&ascending=XXX&ascending=True', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?sort=Q12.Gender&ascending=True', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?sort=Q12.Gender&ascending=True&json_format=records', status.HTTP_200_OK),
        ('/drop/Survey_AI.csv/?filter=Q15.Passed_exams&sort=Q12.Gender&ascending=True&json_format=records', status.HTTP_200_OK),
        ('/drop/Survey_AeI.csv/?filter=Q15.Passed_exams&sort=Q12.Gender&ascending=True&json_format=records', status.HTTP_400_BAD_REQUEST),
    ])
    def test_filter(self, url, status):
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status)

    def test_unauthorized_drop(self):
        response = self.client.delete('/drop/Survey_AI.csv/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @parameterized.expand([
        ('/drop/Survey_AeI.csv/', status.HTTP_400_BAD_REQUEST, 2),
        ('/drop/Survey_AI.csv/', status.HTTP_204_NO_CONTENT, 1),
    ])
    def test_authorized_drop(self, url, status, count):
        token = Token.objects.get(user__username='test_user')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status)
        self.assertEqual(UploadFile.objects.count(), count)