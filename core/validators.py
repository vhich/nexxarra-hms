from django.core.validators import RegexValidator, FileExtensionValidator

phone_validator = RegexValidator(
    regex=r'^\d{9,15}$',
    message="Provide a valid phone number (9–15 digits)."
)

numeric_only_validator = RegexValidator(
    regex=r'^\d+$',
    message="This field must contain digits only."
)

allowed_docs_validator = FileExtensionValidator(
    allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'],
    message="Only jpg, jpeg, png, or pdf files are allowed."
)
