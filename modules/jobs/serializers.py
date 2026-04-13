from rest_framework import serializers

from modules.jobs.models import TinTuyenDung


class TinTuyenDungSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        raw_data = dict(data)

        tieu_de = data.get("tieu_de") or ""
        noi_dung = data.get("noi_dung") or ""
        luong_theo_gio = data.get("luong_theo_gio")
        trang_thai = data.get("trang_thai") or ""
        dia_diem_lam_viec = data.get("dia_diem_lam_viec") or ""

        data["title"] = tieu_de
        data["description"] = noi_dung
        data["summary"] = self._build_summary(noi_dung)
        data["salary"] = self._format_salary(luong_theo_gio)
        data["status"] = self._format_status(trang_thai)
        data["badges"] = self._build_badges(trang_thai, dia_diem_lam_viec)
        data["openings"] = 1
        data["location"] = dia_diem_lam_viec
        data["raw"] = raw_data

        return data

    @staticmethod
    def _build_summary(description):
        summary = (description or "").strip()
        if len(summary) <= 120:
            return summary
        return f"{summary[:117].rstrip()}..."

    @staticmethod
    def _format_salary(salary_value):
        if salary_value in (None, ""):
            return "Chưa cập nhật"
        return f"{salary_value} / giờ"

    @staticmethod
    def _format_status(status_value):
        status_map = {
            TinTuyenDung.TrangThai.DANG_MO: "Đang mở",
            TinTuyenDung.TrangThai.DA_DONG: "Đã đóng",
        }
        return status_map.get(status_value, status_value or "Không xác định")

    @staticmethod
    def _build_badges(status_value, location_value):
        badges = []
        if status_value:
            badges.append(TinTuyenDungSerializer._format_status(status_value))
        if location_value:
            badges.append(location_value)
        return badges or ["Tuyển dụng"]

    class Meta:
        model = TinTuyenDung
        fields = "__all__"


class DangTinTuyenDungFormSerializer(serializers.Serializer):
    tieu_de_cong_viec = serializers.CharField(max_length=255)
    phong_ban = serializers.CharField(max_length=255)
    chuc_danh = serializers.CharField(max_length=255)
    so_luong_tuyen = serializers.IntegerField(min_value=1)
    mo_ta_cong_viec = serializers.CharField()
    nhiem_vu_chinh = serializers.CharField()
    ky_nang = serializers.ListField(
        child=serializers.CharField(max_length=100, allow_blank=False, trim_whitespace=True),
        allow_empty=False,
    )
    yeu_cau_khac = serializers.CharField()
    muc_luong = serializers.CharField(max_length=255)
    thuong_phu_cap = serializers.CharField(max_length=255)
    che_do_khac = serializers.CharField(max_length=255)
    dia_diem_lam_viec = serializers.CharField(max_length=255)
    thoi_gian_lam_viec = serializers.CharField(max_length=255)
    hinh_thuc = serializers.CharField(max_length=255)
    ten_cong_ty = serializers.CharField(max_length=255)
    gioi_thieu_ngan = serializers.CharField(allow_blank=True, required=False, default="")

    def validate_ky_nang(self, value):
        cleaned_skills = []

        for skill in value:
            normalized_skill = skill.strip()
            if normalized_skill:
                cleaned_skills.append(normalized_skill)

        if not cleaned_skills:
            raise serializers.ValidationError("Phai co it nhat mot ky nang hop le.")

        return cleaned_skills

    def validate(self, attrs):
        attrs["phong_ban"] = attrs["phong_ban"].strip()
        attrs["chuc_danh"] = attrs["chuc_danh"].strip()
        attrs["mo_ta_cong_viec"] = attrs["mo_ta_cong_viec"].strip()
        attrs["nhiem_vu_chinh"] = attrs["nhiem_vu_chinh"].strip()
        attrs["yeu_cau_khac"] = attrs["yeu_cau_khac"].strip()
        attrs["muc_luong"] = attrs["muc_luong"].strip()
        attrs["thuong_phu_cap"] = attrs["thuong_phu_cap"].strip()
        attrs["che_do_khac"] = attrs["che_do_khac"].strip()
        attrs["dia_diem_lam_viec"] = attrs["dia_diem_lam_viec"].strip()
        attrs["thoi_gian_lam_viec"] = attrs["thoi_gian_lam_viec"].strip()
        attrs["hinh_thuc"] = attrs["hinh_thuc"].strip()
        attrs["ten_cong_ty"] = attrs["ten_cong_ty"].strip()
        attrs["gioi_thieu_ngan"] = attrs.get("gioi_thieu_ngan", "").strip()

        bat_dau_lam, ket_thuc_lam = self._parse_thoi_gian_lam_viec(attrs["thoi_gian_lam_viec"])
        attrs["bat_dau_lam"] = bat_dau_lam
        attrs["ket_thuc_lam"] = ket_thuc_lam
        return attrs

    @staticmethod
    def _parse_thoi_gian_lam_viec(value):
        normalized_value = (value or "").strip()
        parts = [part.strip() for part in normalized_value.split("-")]

        if len(parts) != 2:
            raise serializers.ValidationError({"thoi_gian_lam_viec": "Dinh dang phai la HH:MM - HH:MM."})

        bat_dau_lam, ket_thuc_lam = parts

        for field_name, time_value in (("bat_dau_lam", bat_dau_lam), ("ket_thuc_lam", ket_thuc_lam)):
            if len(time_value) != 5 or time_value[2] != ":":
                raise serializers.ValidationError({"thoi_gian_lam_viec": "Dinh dang phai la HH:MM - HH:MM."})

            hour_part, minute_part = time_value.split(":", 1)
            if not (hour_part.isdigit() and minute_part.isdigit()):
                raise serializers.ValidationError({"thoi_gian_lam_viec": "Dinh dang phai la HH:MM - HH:MM."})

            hour = int(hour_part)
            minute = int(minute_part)
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                raise serializers.ValidationError({"thoi_gian_lam_viec": "Dinh dang phai la HH:MM - HH:MM."})

        return bat_dau_lam, ket_thuc_lam
