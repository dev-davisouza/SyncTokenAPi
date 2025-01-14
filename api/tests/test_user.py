from django.test import TestCase, Client
from rest_framework import status
from django.contrib.auth.models import User


class AuthAPI(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "admin"
        self.password = "@998833730Dd"
        self.user = User.objects.create_user(
            username=self.username, password=self.password)

    def test_api_jwt_token_is_return_credentials(self):
        response = self.client.post("/api/token/", {
            "username": self.username,
            "password": self.password
        }, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())

    def test_api_jwt_token_does_not_return_credentials(self):
        response = self.client.post("/api/token/", {
            "username": "unathorized user",
            "password": "INCORRECT"
        }, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_returns_unauthorized_stts_code_for_anonymous(self):
        request = self.client.get("/pessoas-all/")
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_jwt_token_can_access_views(self):
        response = self.client.post("/api/token/", {
            "username": self.username,
            "password": self.password
        }, content_type="application/json")

        access_token = response.data["access"]

        """ (HTTP_AUTHORIZATION=f'Bearer ') """
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        request = self.client.get("/pessoas-all/", )

        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_api_jwt_token_can_verifies_access_token(self):
        response = self.client.post("/api/token/", {
            "username": self.username,
            "password": self.password
        }, content_type="application/json")

        access_token = response.data["access"]
        verify_response = self.client.post("/api/token/verify/", {
            "token": access_token
        }, content_type="application/json")
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
