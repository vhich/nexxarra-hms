# Nexxarra HMS

A secure, web-based Hospital Management System (HMS) built with Django and React.  
Designed with **security, compliance, and authenticity protocols** in mind to support real-world healthcare workflows.

---

## 🚀 Features
- Patient registration & consent tracking
- Appointment scheduling & management
- Clinical intake (vital signs, consultations, prescriptions)
- Billing & payments with audit trails
- Clinic verification (license, accreditation, tax ID, proof of address)
- Role-based access control (Doctor, Nurse, Receptionist, Admin)
- Soft delete & audit logging for compliance

---

## 📂 Project Structure
HMS/                # Django project folder
core/               # Main app for models, APIs, workflows
docs/               # Documentation (architecture, workflows, compliance)
README.md           # Project overview
requirements.txt    # Dependencies
.env                # Environment variables (not committed)

---

## 🔐 Security & Compliance
- **Soft deletes**: No hard deletion of medical or financial records.
- **Audit logs**: Every sensitive action is tracked with actor, timestamp, IP, and reason.
- **Clinic verification**: License number, accreditation certificate, tax ID, proof of address required.
- **Patient consent**: Explicit consent must be signed before data use.
- **Environment variables**: Secrets stored in `.env`, never in code.

---

## ⚙️ Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nexxarra-hms.git
   cd nexxarra-hms

2. Create and activate a virtual environment:
    python -m venv venv
    source venv/bin/activate   # Linux/Mac
    venv\Scripts\activate      # Windows

3. Install dependencies:
    pip install -r requirements.txt

4. Create a .env file in the project root:
    SECRET_KEY=your-very-secret-django-key
    DEBUG=True
    DB_NAME=hms_db
    DB_USER=hms_user
    DB_PASSWORD=supersecurepassword
    DB_HOST=localhost
    DB_PORT=5432
    ALLOWED_HOSTS=localhost,127.0.0.1

5. Run migrations:
    python manage.py migrate

6. Start the development server:
    python manage.py runserver


 ## 📖 Documentation
See the docs/ folder for:

architecture.md → system design notes

workflows.md → patient & clinic workflows

compliance.md → security & legal compliance protocols

## 🧭 Roadmap
Add React frontend

Implement role-based dashboards

Integrate external APIs for clinic license verification

Deploy to cloud with secure CI/CD

## ⚠️ Disclaimer
This project is for educational and portfolio purposes.
In real-world healthcare deployments, additional compliance with local laws (e.g., NDPA in Nigeria) and international standards (HIPAA, GDPR) is required.
