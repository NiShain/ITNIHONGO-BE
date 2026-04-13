from django.urls import path
from rest_framework.routers import DefaultRouter

from modules.jobs.views import DangTinTuyenDungFormView, TinTuyenDungViewSet

router = DefaultRouter()
router.register(r"posts", TinTuyenDungViewSet, basename="job-posts")

urlpatterns = [
	path("posts/intake/", DangTinTuyenDungFormView.as_view(), name="job-post-intake"),
] + router.urls
