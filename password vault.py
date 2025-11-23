import json, os, getpass, hashlib
from base64 import b64encode, b64decode
vault_file = "passwords.json"
master_file = "master.key"
print("\n Password Vault\n")
# Check if vault exists
if os.path.exists(master_file):
    master_password = getpass.getpass("Master Password (or type 'reset' to reset): ")
    if master_password.lower() == 'reset':
        print("\n  WARNING: Resetting will DELETE all saved passwords!")
        confirm = input("Type 'DELETE' to confirm: ")
        if confirm == 'DELETE':
            os.remove(master_file)
            if os.path.exists(vault_file):
                os.remove(vault_file)
            print(" Vault reset! Run again to create new vault.\n")
        else:
            print(" Reset cancelled!")
        exit()
    stored_hash = open(master_file, 'r').read()
    password_hash = hashlib.sha256(master_password.encode()).hexdigest()
    if password_hash != stored_hash:
        print(" Wrong password!")
        print(" Tip: Type 'reset' to reset vault (will delete all passwords)")
        exit()
    print("Unlocked!\n")
else:
    master_password = getpass.getpass("Create Master Password: ")
    confirm = getpass.getpass("Confirm: ")
    if master_password != confirm:
        print(" Passwords don't match!")
        exit()
    password_hash = hashlib.sha256(master_password.encode()).hexdigest()
    open(master_file, 'w').write(password_hash)
    print(" Vault created!\n")

# Load existing passwords
if os.path.exists(vault_file):
    encrypted = open(vault_file, 'r').read()
    if encrypted:
        data = b64decode(encrypted.encode()).decode('latin-1')
        key = (master_password * (len(data) // len(master_password) + 1))[:len(data)]
        decrypted = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(data, key))
        passwords = json.loads(decrypted)
    else:
        passwords = {}
else:
    passwords = {}

# Main menu
while True:
    print("1.  Add   2.  View   3.  List   4.  Delete   5.  Reset   6.  Exit")
    choice = input("Your choice: ")
    if choice == '1':
        service = input("\nService name: ")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        passwords[service] = {"username": username, "password": password}
        data = json.dumps(passwords)
        key = (master_password * (len(data) // len(master_password) + 1))[:len(data)]
        encrypted = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(data, key))
        encrypted_final = b64encode(encrypted.encode('latin-1')).decode()
        open(vault_file, 'w').write(encrypted_final)
        print(f" {service} saved!\n")
    elif choice == '2':
        if not passwords:
            print("\n📭 Vault is empty!\n")
        else:
            service = input("\nService name: ")
            if service in passwords:
                print(f"\nUsername: {passwords[service]['username']}")
                print(f"Password: {passwords[service]['password']}\n")
            else:
                print(f" {service} not found!\n")
    elif choice == '3':
        if not passwords:
            print("\n📭 Vault is empty!\n")
        else:
            print(f"\n Your saved passwords ({len(passwords)}):")
            for service in sorted(passwords.keys()):
                print(f"  • {service} - {passwords[service]['username']}")
            print()
    elif choice == '4':
        if not passwords:
            print("\n📭 Vault is empty!\n")
        else:
            service = input("\nService to delete: ")
            if service in passwords:
                confirm = input(f"Delete {service}? (yes/no): ")
                if confirm.lower() == 'yes':
                    del passwords[service]
                    data = json.dumps(passwords)
                    key = (master_password * (len(data) // len(master_password) + 1))[:len(data)]
                    encrypted = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(data, key))
                    encrypted_final = b64encode(encrypted.encode('latin-1')).decode()
                    open(vault_file, 'w').write(encrypted_final)
                    print(f" {service} deleted!\n")
                else:
                    print(" Cancelled!\n")
            else:
                print(f" {service} not found!\n")
    elif choice == '5':
        print("\n Reset Master Password")
        old_password = getpass.getpass("Current Master Password: ")
        old_hash = hashlib.sha256(old_password.encode()).hexdigest()
        if old_hash != stored_hash:
            print(" Wrong password! Can't reset.\n")
        else:
            new_password = getpass.getpass("New Master Password: ")
            confirm = getpass.getpass("Confirm New Password: ")
            if new_password != confirm:
                print(" Passwords don't match!\n")
            else:
                # Save new master password hash
                new_hash = hashlib.sha256(new_password.encode()).hexdigest()
                open(master_file, 'w').write(new_hash)
                
                if passwords:
                    data = json.dumps(passwords)
                    key = (new_password * (len(data) // len(new_password) + 1))[:len(data)]
                    encrypted = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(data, key))
                    encrypted_final = b64encode(encrypted.encode('latin-1')).decode()
                    open(vault_file, 'w').write(encrypted_final)
                master_password = new_password
                stored_hash = new_hash
                print(" Master password reset successfully!\n")
    
    elif choice == '6':
        print("\n Vault locked! Bye! \n")
        break
    
    else:
        print(" Invalid choice!\n")