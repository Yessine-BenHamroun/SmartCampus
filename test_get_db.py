import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcampus.settings')
django.setup()

from Learner.models import get_db

print("=== Test de get_db() ===")
db = get_db()
print(f"Nom de la base: {db.name}")

print("\n=== Recherche des étudiants ===")
students = list(db.users.find({'role': 'student'}))
print(f"Nombre d'étudiants trouvés: {len(students)}")

for student in students:
    print(f"\nÉtudiant:")
    print(f"  - Email: {student.get('email')}")
    print(f"  - Username: {student.get('username')}")
    print(f"  - First name: {student.get('first_name')}")
    print(f"  - Last name: {student.get('last_name')}")
    print(f"  - Role: {student.get('role')}")
