import imaplib
import email
import smtplib
import requests

# Gmail giriş bilgileri
EMAIL_USER = "aliilhanege@gmail.com"  # Buraya kendi e-posta adresini yaz
EMAIL_PASS = "google_app_password"  # Google'dan aldığın uygulama şifresini buraya yaz

# Hugging Face API Anahtarı
HUGGING_FACE_API_KEY = "huggingface_api_key"  # Hugging Face API anahtarınızı buraya ekleyin

# Yanıt verilecek e-posta adresi (sadece bu kişiden gelen e-postalara yanıt verilecek)
ALLOWED_SENDER = "belirli_kisi@gmail.com"

# Gelen e-postaları oku
def check_email():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")

    _, data = mail.search(None, "UNSEEN")  # Sadece okunmamış e-postaları al
    email_ids = data[0].split()

    for e_id in email_ids:
        _, msg_data = mail.fetch(e_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        sender = msg["From"]
        subject = msg["Subject"]
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8")
        else:
            body = msg.get_payload(decode=True).decode("utf-8")

        print(f"Gelen e-posta: {sender} - {subject}")

        # Sadece belirlenen kişiden gelen e-postalara AI yanıtı oluştur
        if ALLOWED_SENDER in sender:
            reply = generate_ai_response(body)
            send_email(sender, reply)
        else:
            print("Bu e-posta yanıtsız bırakıldı.")

    mail.logout()

# Hugging Face API ile yanıt oluştur
def generate_ai_response(text):
    url = "https://api-inference.huggingface.co/models/gpt2"
    headers = {
        "Authorization": f"Bearer {HUGGING_FACE_API_KEY}"
    }
    payload = {
        "inputs": text
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result[0]["generated_text"].strip()
    else:
        return "Üzgünüm, bir hata oluştu."

# Yanıtı e-posta ile gönder
def send_email(to_email, reply_text):
    msg = email.message.EmailMessage()
    msg.set_content(reply_text)
    msg["Subject"] = "Re: Otomatik Yanıt"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print(f"Yanıt gönderildi: {to_email}")

# Botu çalıştır
check_email()
