from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from modules.accounts.models import NguoiDung


@override_settings(
	TEST_TOKEN_ENDPOINT_ENABLED=True,
	TEST_TOKEN_EMAIL="sprint-test@example.com",
	TEST_TOKEN_ROLE="cong_ty",
	TEST_TOKEN_PASSWORD="token-password",
	TEST_TOKEN_SHARED_SECRET="sprint-secret",
)
class TestTokenEndpointTests(APITestCase):
	def test_requires_shared_secret_when_configured(self):
		response = self.client.post("/api/auth/test-token/", format="json")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_returns_access_and_refresh_tokens(self):
		response = self.client.post(
			"/api/auth/test-token/",
			format="json",
			HTTP_X_TEST_TOKEN_SECRET="sprint-secret",
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn("access", response.data)
		self.assertIn("refresh", response.data)
		self.assertEqual(response.data["token_type"], "Bearer")
		self.assertEqual(response.data["user"]["email"], "sprint-test@example.com")

		user = NguoiDung.objects.get(email="sprint-test@example.com")
		self.assertEqual(response.data["user"]["id"], user.id)

	def test_generated_access_token_can_call_protected_endpoint(self):
		token_response = self.client.post(
			"/api/auth/test-token/",
			format="json",
			HTTP_X_TEST_TOKEN_SECRET="sprint-secret",
		)
		access = token_response.data["access"]

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
		protected_response = self.client.get("/api/accounts/users/")
		self.assertEqual(protected_response.status_code, status.HTTP_200_OK)

	def test_accepts_role_from_request(self):
		response = self.client.post(
			"/api/auth/test-token/",
			{"vai_tro": "ung_vien"},
			format="json",
			HTTP_X_TEST_TOKEN_SECRET="sprint-secret",
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["user"]["vai_tro"], "ung_vien")

		user = NguoiDung.objects.get(email="sprint-test@example.com")
		self.assertEqual(user.vai_tro, "ung_vien")

	def test_rejects_invalid_role(self):
		response = self.client.post(
			"/api/auth/test-token/",
			{"role": "invalid-role"},
			format="json",
			HTTP_X_TEST_TOKEN_SECRET="sprint-secret",
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("allowed_roles", response.data)


@override_settings(TEST_TOKEN_ENDPOINT_ENABLED=False)
class TestTokenEndpointDisabledTests(APITestCase):
	def test_returns_not_found_when_disabled(self):
		response = self.client.post("/api/auth/test-token/", format="json")
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
