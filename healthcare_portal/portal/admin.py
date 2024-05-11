from django.contrib import admin

from .models import Answer, Appointment, CustomUser, Question

admin.site.register(Question)
admin.site.register(Answer)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "username",
        "first_name",
        "last_name",
        "user_type",
        "is_active",
        "is_staff",
        "availability",
    )
    list_filter = ("user_type", "is_active", "is_superuser")

    fieldsets = (
        (None, {"fields": ("username", "user_type", "availability")}),
        (("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("appointment_info", "appointment_completed")

    def appointment_info(self, obj):
        return (
            f"Appointment for {obj.patient.first_name} with Dr. {obj.doctor.first_name}"
        )

    appointment_info.short_description = "Appointment Info"


admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
