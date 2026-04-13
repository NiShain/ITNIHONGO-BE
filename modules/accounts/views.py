from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from modules.accounts.models import NguoiDung
from modules.accounts.serializers import NguoiDungSerializer


class NguoiDungViewSet(viewsets.ModelViewSet):
	queryset = NguoiDung.objects.all().order_by("id")
	serializer_class = NguoiDungSerializer

	def get_permissions(self):
		if self.action == "create":
			return [AllowAny()]
		return [IsAuthenticated()]


class TestTokenView(APIView):
	permission_classes = [AllowAny]
	authentication_classes = []

	def post(self, request):
		if not settings.TEST_TOKEN_ENDPOINT_ENABLED:
			raise NotFound("Test token endpoint is disabled")

		shared_secret = settings.TEST_TOKEN_SHARED_SECRET
		if shared_secret:
			request_secret = request.headers.get("X-Test-Token-Secret", "")
			if request_secret != shared_secret:
				raise PermissionDenied("Invalid shared secret")

		requested_role = request.data.get("vai_tro") or request.data.get("role")
		allowed_roles = {choice[0] for choice in NguoiDung.VaiTro.choices}
		role = requested_role or settings.TEST_TOKEN_ROLE
		if role not in allowed_roles:
			return Response(
				{"detail": "Invalid role", "allowed_roles": sorted(allowed_roles)},
				status=status.HTTP_400_BAD_REQUEST,
			)

		user, created = NguoiDung.objects.get_or_create(
			email=settings.TEST_TOKEN_EMAIL,
			defaults={
				"vai_tro": role,
				"is_active": True,
			},
		)

		fields_to_update = []
		if created:
			user.set_password(settings.TEST_TOKEN_PASSWORD)
			fields_to_update.append("password")
		if not user.is_active:
			user.is_active = True
			fields_to_update.append("is_active")
		if user.vai_tro != role:
			user.vai_tro = role
			fields_to_update.append("vai_tro")
		if fields_to_update:
			user.save(update_fields=fields_to_update)

		refresh = RefreshToken.for_user(user)
		return Response(
			{
				"access": str(refresh.access_token),
				"refresh": str(refresh),
				"token_type": "Bearer",
				"user": {
					"id": user.id,
					"email": user.email,
					"vai_tro": user.vai_tro,
				},
			},
			status=status.HTTP_200_OK,
		)
