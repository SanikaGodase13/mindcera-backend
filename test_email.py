from app.services.email_service import send_otp_email

send_otp_email(
    "sanikagodase13@gmail.com",
    "123456"
)

print("Email Sent")