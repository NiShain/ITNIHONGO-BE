from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from modules.jobs.models import TinTuyenDung
from modules.profiles.models import HoSoCongTy


class TinTuyenDungViewSetTests(APITestCase):
	def setUp(self):
		self.list_url = reverse("job-posts-list")
		self.intake_url = reverse("job-post-intake")
		user_model = get_user_model()
		self.company_user = user_model.objects.create_user(
			email="company@example.com",
			password="password123",
			vai_tro=user_model.VaiTro.CONG_TY,
		)
		self.company_profile = HoSoCongTy.objects.create(
			cong_ty=self.company_user,
			ten_cong_ty="Cong Ty ABC",
			linh_vuc="Cong nghe",
			dia_chi="Da Nang",
		)

		start_time = timezone.now()
		end_time = start_time + timedelta(days=30)

		self.open_job = TinTuyenDung.objects.create(
			cong_ty=self.company_profile,
			tieu_de="Lập trình viên Python",
			noi_dung="Tuyển lập trình viên Python làm việc với Django REST API.",
			bat_dau_lam=start_time,
			ket_thuc_lam=end_time,
			luong_theo_gio=Decimal("120.00"),
			dia_diem_lam_viec="Da Nang",
			trang_thai=TinTuyenDung.TrangThai.DANG_MO,
		)
		self.closed_job = TinTuyenDung.objects.create(
			cong_ty=self.company_profile,
			tieu_de="Nhân viên hỗ trợ",
			noi_dung="Công việc hỗ trợ nội bộ cho doanh nghiệp.",
			bat_dau_lam=start_time,
			ket_thuc_lam=end_time,
			luong_theo_gio=Decimal("80.00"),
			dia_diem_lam_viec="Hue",
			trang_thai=TinTuyenDung.TrangThai.DA_DONG,
		)

	def test_list_is_public_and_returns_only_open_jobs_by_default(self):
		response = self.client.get(self.list_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		payload = response.data[0]
		self.assertEqual(payload["tin_id"], self.open_job.tin_id)
		self.assertEqual(payload["trang_thai"], TinTuyenDung.TrangThai.DANG_MO)
		self.assertEqual(payload["title"], self.open_job.tieu_de)
		self.assertEqual(payload["description"], self.open_job.noi_dung)
		self.assertEqual(payload["summary"], self.open_job.noi_dung)
		self.assertEqual(payload["salary"], "120.00 / giờ")
		self.assertEqual(payload["status"], "Đang mở")
		self.assertEqual(payload["openings"], 1)
		self.assertEqual(payload["location"], self.open_job.dia_diem_lam_viec)
		self.assertIn("raw", payload)
		self.assertEqual(payload["raw"]["tin_id"], self.open_job.tin_id)
		self.assertEqual(payload["raw"]["tieu_de"], self.open_job.tieu_de)

	def test_list_can_filter_by_keyword(self):
		response = self.client.get(self.list_url, {"q": "python"})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["tin_id"], self.open_job.tin_id)
		self.assertEqual(response.data[0]["summary"], self.open_job.noi_dung)

	def test_list_can_filter_by_location(self):
		response = self.client.get(self.list_url, {"dia_diem": "da nang"})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["tin_id"], self.open_job.tin_id)

	def test_list_can_filter_by_salary(self):
		response = self.client.get(self.list_url, {"luong_min": "100"})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["tin_id"], self.open_job.tin_id)

	def test_list_can_filter_by_status(self):
		response = self.client.get(self.list_url, {"trang_thai": TinTuyenDung.TrangThai.DA_DONG})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["tin_id"], self.closed_job.tin_id)

	def test_list_returns_bad_request_for_invalid_salary(self):
		response = self.client.get(self.list_url, {"luong_min": "abc"})

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("luong_min", response.data)

	def test_intake_endpoint_accepts_form_payload_for_company_users(self):
		self.client.force_authenticate(user=self.company_user)
		payload = {
			"tieu_de_cong_viec": "ReactJS Front-end Developer",
			"phong_ban": "Sản phẩm",
			"chuc_danh": "Front-end Developer",
			"so_luong_tuyen": 2,
			"mo_ta_cong_viec": "Xây dựng giao diện React cho sản phẩm nội bộ.",
			"nhiem_vu_chinh": "Phát triển tính năng mới, tối ưu giao diện và xử lý dữ liệu từ API.",
			"ky_nang": ["ReactJS", "HTML/CSS", "REST API"],
			"yeu_cau_khac": "Ưu tiên ứng viên có kinh nghiệm làm việc với sản phẩm nội bộ.",
			"muc_luong": "Thoả thuận",
			"thuong_phu_cap": "Thưởng theo dự án",
			"che_do_khac": "Đào tạo nội bộ, bảo hiểm đầy đủ, review định kỳ.",
			"dia_diem_lam_viec": "TP. Hồ Chí Minh",
			"thoi_gian_lam_viec": "09:00 - 18:00",
			"hinh_thuc": "Hybrid",
			"ten_cong_ty": "Công ty công nghệ nội bộ",
			"gioi_thieu_ngan": "Môi trường làm việc tập trung vào sản phẩm.",
		}

		response = self.client.post(self.intake_url, payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["message"], "Da nhan du lieu dang tin.")
		self.assertEqual(response.data["data"]["tieu_de_cong_viec"], payload["tieu_de_cong_viec"])
		self.assertEqual(response.data["data"]["ky_nang"], payload["ky_nang"])
		self.assertEqual(response.data["data"]["thoi_gian_lam_viec"], payload["thoi_gian_lam_viec"])
		self.assertEqual(response.data["data"]["bat_dau_lam"], "09:00")
		self.assertEqual(response.data["data"]["ket_thuc_lam"], "18:00")
		self.assertEqual(response.data["data"]["cong_ty_id"], self.company_profile.cong_ty_id)

	def test_intake_endpoint_rejects_invalid_time_range_format(self):
		self.client.force_authenticate(user=self.company_user)
		payload = {
			"tieu_de_cong_viec": "ReactJS Front-end Developer",
			"phong_ban": "Sản phẩm",
			"chuc_danh": "Front-end Developer",
			"so_luong_tuyen": 2,
			"mo_ta_cong_viec": "Xây dựng giao diện React cho sản phẩm nội bộ.",
			"nhiem_vu_chinh": "Phát triển tính năng mới, tối ưu giao diện và xử lý dữ liệu từ API.",
			"ky_nang": ["ReactJS", "HTML/CSS", "REST API"],
			"yeu_cau_khac": "Ưu tiên ứng viên có kinh nghiệm làm việc với sản phẩm nội bộ.",
			"muc_luong": "Thoả thuận",
			"thuong_phu_cap": "Thưởng theo dự án",
			"che_do_khac": "Đào tạo nội bộ, bảo hiểm đầy đủ, review định kỳ.",
			"dia_diem_lam_viec": "TP. Hồ Chí Minh",
			"thoi_gian_lam_viec": "09:00 to 18:00",
			"hinh_thuc": "Hybrid",
			"ten_cong_ty": "Công ty công nghệ nội bộ",
			"gioi_thieu_ngan": "Môi trường làm việc tập trung vào sản phẩm.",
		}

		response = self.client.post(self.intake_url, payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("thoi_gian_lam_viec", response.data)
