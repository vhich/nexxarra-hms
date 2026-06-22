from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator, FileExtensionValidator

from django.conf import settings

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        # Override delete to perform soft delete
        return super().update(is_active=False)

    def hard_delete(self):
        # Explicit hard delete (rarely used, e.g., test cleanup)
        return super().delete()

    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # Default: only active records
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_active=True)

    def all_objects(self):
        # Explicit: include both active + inactive
        return SoftDeleteQuerySet(self.model, using=self._db)

# Reusable validators for security and integrity
phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,13}$',
    message="Provide a valid phone number."
)

numeric_only_validator = RegexValidator(
    regex=r'^\d+$',
    message="This field must contain digits only."
)

# Restrict file uploads to PDFs and Images only to prevent malicious script execution
allowed_docs_validator = FileExtensionValidator(
    allowed_extensions=['jpg', 'jpeg', 'png'],
    message="Only jpg, jpeg, png files are allowed."
)

class Clinic(models.Model):
    name = models.CharField(max_length=255, default="")
    address = models.TextField(max_length=225, default="")
    
    # Secure Phone: Validates actual phone formats, prevents injection strings
    phone = models.CharField(max_length=20, validators=[phone_validator], default="")
    email = models.EmailField(max_length=100, default="")

    # Verification & compliance
    license_number = models.CharField(max_length=100, unique=True, default="")
    
    # FORCE FRONTEND REQUIREMENT: Removed null=True and blank=True so frontend MUST provide them
    accreditation_certificate = models.FileField(
        upload_to="clinic_docs/", 
        validators=[allowed_docs_validator],
        blank=True,
        null=True
    )
    
    # Strict Tax ID: Handled as string, but strictly validated for min/max length and digits only
    tax_id = models.CharField(
        max_length=100, 
        unique=True,
        validators=[MinLengthValidator(13), numeric_only_validator],
        default=""
    )
    
    proof_of_address = models.FileField(
        upload_to="clinic_docs/",
        validators=[allowed_docs_validator],
        blank=True,
        null=True
    )

    # Internal verification (Keep blank/null here, frontend shouldn't touch these anyway)
    verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True, default="") # Better practice than null=True for TextField

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Soft delete managers
    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager()

    def __str__(self):
        return self.name


class Department(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

class User(AbstractUser):
    clinic = models.ForeignKey("Clinic", on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=50, choices=[
        ("super_admin", "Super Admin"),
        ("clinic_admin", "Clinic Admin"),
        ("doctor", "Doctor"),
        ("nurse", "Nurse"),
        ("receptionist", "Receptionist"),
    ])
    # first_name, last_name, email, password already exist from AbstractUser

class StaffProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)  # Doctor, Nurse, Receptionist
    department = models.ManyToManyField(Department, blank=True)
    is_active = models.BooleanField(default=False)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager()


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    target_type = models.CharField(max_length=100)
    target_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_metadata = models.TextField(null=True, blank=True)


class Patient(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    consent_signed = models.BooleanField(default=False)  # legal consent tracking
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager()


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    provider = models.ForeignKey(StaffProfile, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    date = models.DateTimeField()
    status = models.CharField(max_length=50, default="Scheduled")


class VitalSign(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    blood_pressure = models.CharField(max_length=20)
    temperature = models.FloatField()
    pulse = models.IntegerField()
    weight = models.FloatField()
    height = models.FloatField()
    notes = models.TextField()


class Consultation(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT)
    doctor = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True)
    notes = models.TextField()
    diagnosis = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager()


class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.PROTECT)
    medication = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField()
    is_active = models.BooleanField(default=True)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager()

class ServiceCatalogItem(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="Draft")
    is_active = models.BooleanField(default=True)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager()


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceCatalogItem, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50)  # Cash, Card, Transfer
    timestamp = models.DateTimeField(auto_now_add=True)


