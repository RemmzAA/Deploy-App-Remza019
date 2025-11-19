"""
019Solutions - Environment Variable Encryption
Encrypt sensitive .env files for production deployment
"""
from cryptography.fernet import Fernet
import os
import sys

def generate_key():
    """Generate encryption key (run once, save securely!)"""
    key = Fernet.generate_key()
    print("=" * 60)
    print("ENCRYPTION KEY GENERATED")
    print("=" * 60)
    print(f"\n{key.decode()}\n")
    print("=" * 60)
    print("⚠️  SAVE THIS KEY SECURELY!")
    print("⚠️  Add to deployment platform as ENCRYPTION_KEY env var")
    print("⚠️  NEVER commit this key to Git!")
    print("=" * 60)
    return key

def encrypt_env_file(env_path='.env', output_path='.env.encrypted', key=None):
    """Encrypt .env file"""
    if not os.path.exists(env_path):
        print(f"❌ Error: {env_path} not found")
        return False
    
    if key is None:
        print("❌ Error: Encryption key required")
        return False
    
    # Read .env file
    with open(env_path, 'rb') as f:
        env_data = f.read()
    
    # Encrypt
    fernet = Fernet(key if isinstance(key, bytes) else key.encode())
    encrypted_data = fernet.encrypt(env_data)
    
    # Write encrypted file
    with open(output_path, 'wb') as f:
        f.write(encrypted_data)
    
    print(f"✅ Encrypted: {env_path} → {output_path}")
    print(f"✅ Size: {len(env_data)} bytes → {len(encrypted_data)} bytes")
    return True

def decrypt_env_file(encrypted_path='.env.encrypted', output_path='.env', key=None):
    """Decrypt .env.encrypted file"""
    if not os.path.exists(encrypted_path):
        print(f"❌ Error: {encrypted_path} not found")
        return False
    
    if key is None:
        print("❌ Error: Decryption key required")
        return False
    
    # Read encrypted file
    with open(encrypted_path, 'rb') as f:
        encrypted_data = f.read()
    
    # Decrypt
    try:
        fernet = Fernet(key if isinstance(key, bytes) else key.encode())
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        return False
    
    # Write decrypted file
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)
    
    print(f"✅ Decrypted: {encrypted_path} → {output_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
019Solutions Environment Encryption Tool

Usage:
    python encrypt_env.py generate              # Generate encryption key
    python encrypt_env.py encrypt <key>         # Encrypt .env file
    python encrypt_env.py decrypt <key>         # Decrypt .env.encrypted file
    
Example:
    python encrypt_env.py generate
    python encrypt_env.py encrypt "your-key-here"
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "generate":
        generate_key()
    
    elif command == "encrypt":
        if len(sys.argv) < 3:
            print("❌ Error: Encryption key required")
            print("Usage: python encrypt_env.py encrypt <key>")
            sys.exit(1)
        
        key = sys.argv[2]
        encrypt_env_file(key=key)
        print("\n⚠️  NEXT STEPS:")
        print("1. Delete original .env file (optional, for max security)")
        print("2. Add ENCRYPTION_KEY to deployment platform")
        print("3. Update server.py to load from .env.encrypted")
    
    elif command == "decrypt":
        if len(sys.argv) < 3:
            print("❌ Error: Decryption key required")
            print("Usage: python encrypt_env.py decrypt <key>")
            sys.exit(1)
        
        key = sys.argv[2]
        decrypt_env_file(key=key)
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
