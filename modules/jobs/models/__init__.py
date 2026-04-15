from django.db import models


class TinTuyenDung(models.Model):
	class TrangThai(models.TextChoices):
		DANG_MO = "dang_mo", "Dang mo"
		DA_DONG = "da_dong", "Da dong"

	tin_id = models.AutoField(primary_key=True)
	cong_ty = models.ForeignKey(
		"profiles.HoSoCongTy",
		on_delete=models.CASCADE,
		db_column="cong_ty_id",
		related_name="tin_tuyen_dung",
	)
	tieu_de = models.CharField(max_length=255)
	noi_dung = models.TextField()
	bat_dau_lam = models.DateTimeField()
	ket_thuc_lam = models.DateTimeField()
	luong_theo_gio = models.DecimalField(max_digits=10, decimal_places=2)
	dia_diem_lam_viec = models.CharField(max_length=255)
	hinh_thuc_tuyen_dung = models.CharField(max_length=255, null=True, blank=True)
	yeu_cau = models.TextField(null=True, blank=True)
	quyen_loi = models.TextField(null=True, blank=True)
	trang_thai = models.CharField(max_length=20, choices=TrangThai.choices, default=TrangThai.DANG_MO)
	tao_luc = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "TIN_TUYEN_DUNG"
