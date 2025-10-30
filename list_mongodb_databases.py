from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Lister toutes les bases de données
print("=== Bases de données disponibles ===")
db_list = client.list_database_names()
for db_name in db_list:
    print(f"  - {db_name}")

# Vérifier dans chaque base
for db_name in db_list:
    if db_name not in ['admin', 'config', 'local']:
        print(f"\n=== Base de données: {db_name} ===")
        db = client[db_name]
        collections = db.list_collection_names()
        print(f"Collections: {collections}")
        
        if 'users' in collections:
            users_count = db.users.count_documents({})
            print(f"  users collection: {users_count} documents")
            
            if users_count > 0:
                # Afficher quelques exemples
                print("\n  Exemples d'utilisateurs:")
                for user in db.users.find().limit(3):
                    print(f"    - Email: {user.get('email')}, Role: {user.get('role')}, Username: {user.get('username')}")
