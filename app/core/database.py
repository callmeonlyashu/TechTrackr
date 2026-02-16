import asyncio
import ssl
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Key Vault Details
VAULT_URL = "https://techtrackr-vault.vault.azure.net/"

def _get_keyvault_secret(secret_name: str) -> str:
    """Retrieve secret and immediately strip whitespace."""
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=VAULT_URL, credential=credential)
    # .strip() prevents 'nodename not known' errors caused by hidden spaces
    return client.get_secret(secret_name).value.strip()

def get_database_url() -> str:
    """Construct a sanitized connection string."""
    db_user = _get_keyvault_secret("techtrackr-db-user-dev-001")
    db_pass = _get_keyvault_secret("techtrackr-db-password-dev")
    db_host = _get_keyvault_secret("techtrackr-dev-host-dev")
    db_port = _get_keyvault_secret("techtrackr-db-port-dev")
    
    # Remove https:// or trailing slashes that might be in the Vault
    clean_host = db_host.replace("https://", "").replace("http://", "").split("/")[0]
    
    print(f"DEBUG: Resolving Host: |{clean_host}|")
    
    return f"postgresql+asyncpg://{db_user}:{db_pass}@{clean_host}:{db_port}/postgres"

# Setup SSL Context to allow Azure's certificates
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    get_database_url(),
    connect_args={"ssl": ssl_ctx},
    pool_pre_ping=True
)

async def check_db_connection():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("Success: TechTrackr is connected to Azure Postgres!")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_db_connection())