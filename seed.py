from app.database import SessionLocal, init_db
from app.models import Role, User, FileRecord, Permission

def seed():
    init_db()
    db = SessionLocal()
    try:
        if db.query(User).count():
            print("Database already seeded.")
            return

        roles = [Role(name=x) for x in ["HR Executive", "Finance Executive", "Developer", "Manager"]]
        db.add_all(roles); db.commit()

        users = [
            User(name="Rahul Sharma", email="rahul@dataguard.local", department="HR", role_id=roles[0].id),
            User(name="Priya Verma", email="priya@dataguard.local", department="Finance", role_id=roles[1].id),
            User(name="Amit Singh", email="amit@dataguard.local", department="IT", role_id=roles[2].id),
            User(name="Neha Patel", email="neha@dataguard.local", department="HR", role_id=roles[3].id),
        ]
        db.add_all(users); db.commit()

        files = [
            FileRecord(name="company_logo.png", classification="PUBLIC", owner_department="Marketing"),
            FileRecord(name="employee_policy.pdf", classification="INTERNAL", owner_department="HR"),
            FileRecord(name="employee_salary.xlsx", classification="CONFIDENTIAL", owner_department="HR"),
            FileRecord(name="patient_records.xlsx", classification="HIGHLY_SENSITIVE", owner_department="Medical"),
            FileRecord(name="company_database.sql", classification="CRITICAL", owner_department="IT"),
            FileRecord(name="quarterly_financial_report.xlsx", classification="CONFIDENTIAL", owner_department="Finance"),
        ]
        db.add_all(files); db.commit()

        permissions = [
            Permission(user_id=users[0].id, file_id=files[1].id, can_read=True, can_download=True),
            Permission(user_id=users[1].id, file_id=files[5].id, can_read=True, can_download=True, can_share=True),
            Permission(user_id=users[2].id, file_id=files[4].id, can_read=True, can_download=True),
            Permission(user_id=users[3].id, file_id=files[1].id, can_read=True, can_download=True, can_share=True, can_copy=True),
            Permission(user_id=users[3].id, file_id=files[2].id, can_read=True, can_download=True, can_share=True, can_copy=True),
        ]
        db.add_all(permissions); db.commit()

        print("Seed complete.")
        print("Users: 1 Rahul, 2 Priya, 3 Amit, 4 Neha")
        print("Files: 1 logo, 2 policy, 3 salary, 4 patient records, 5 database, 6 financial report")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
