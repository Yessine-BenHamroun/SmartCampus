from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['smartcampus_db']  # ✅ Nom correct de la base

# Vérifier les utilisateurs avec role='student'
print("=== Recherche des étudiants ===")
students = list(db.users.find({'role': 'student'}))
print(f"Nombre d'étudiants trouvés: {len(students)}")

for student in students:
    print(f"\nÉtudiant:")
    print(f"  - Email: {student.get('email')}")
    print(f"  - Username: {student.get('username')}")
    print(f"  - First name: {student.get('first_name')}")
    print(f"  - Last name: {student.get('last_name')}")
    print(f"  - Role: {student.get('role')}")
    print(f"  - Active: {student.get('is_active')}")

# Vérifier tous les utilisateurs
print("\n\n=== Tous les utilisateurs ===")
all_users = list(db.users.find())
print(f"Nombre total d'utilisateurs: {len(all_users)}")

for user in all_users:
    print(f"\nUtilisateur:")
    print(f"  - Email: {user.get('email')}")
    print(f"  - Username: {user.get('username')}")
    print(f"  - Role: {user.get('role')}")
    print(f"  - Active: {user.get('is_active')}")
