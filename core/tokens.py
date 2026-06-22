from django.contrib.auth.tokens import PasswordResetTokenGenerator

token_generator = PasswordResetTokenGenerator()

def generate_activation_token(user):
    return token_generator.make_token(user)

