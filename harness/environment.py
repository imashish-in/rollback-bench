import sqlite3
import os
import shutil
import json
from typing import Dict, Any, List

class RollbackEnvironment:
    """Manages isolated state execution, failure injection, and ground-truth auditing."""
    
    def __init__(self, sandbox_dir: str = "/tmp/rollback_sandbox"):
        self.sandbox_dir = sandbox_dir
        self.db_path = os.path.join(self.sandbox_dir, "environment.db")
        self.executed_mutations: List[str] = []
        self.reset_environment()

    def reset_environment(self):
        """Restores the sandbox back to pristine State S_0."""
        if os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir)
        os.makedirs(self.sandbox_dir, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE users (id TEXT PRIMARY KEY, status TEXT)")
        conn.commit()
        conn.close()
        self.executed_mutations = []

    # --- MOCK TOOLS WITH EXPLICIT DOCSTRINGS FOR OLLAMA ---

    def create_user_record(self, user_id: str) -> str:
        """Creates a database record for a user in the SQL database.
        
        Args:
            user_id: The unique identifier for the user (e.g. 'usr_404').
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (id, status) VALUES (?, ?)", (user_id, "PENDING"))
        conn.commit()
        conn.close()
        self.executed_mutations.append(f"DB_CREATE:{user_id}")
        return f"SUCCESS: Created database record for {user_id}"

    def delete_user_record(self, user_id: str) -> str:
        """Deletes/reverts a user database record from the SQL database.
        
        Args:
            user_id: The unique identifier for the user to remove.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        self.executed_mutations.append(f"DB_DELETE:{user_id}")
        return f"SUCCESS: Deleted database record for {user_id}"

    def create_config_file(self, filename: str, content: Any) -> str:
        filepath = os.path.join(self.sandbox_dir, filename)
        
        # Auto-convert dict/list inputs into valid JSON strings
        if isinstance(content, (dict, list)):
            content = json.dumps(content, indent=2)
        elif not isinstance(content, str):
            content = str(content)

        with open(filepath, "w") as f:
            f.write(content)
            
        self.executed_mutations.append(f"FILE_CREATE:{filename}")
        return f"SUCCESS: Created local file {filename}"

    def delete_config_file(self, filename: str) -> str:
        """Deletes a local configuration file from disk.
        
        Args:
            filename: The file name to delete.
        """
        filepath = os.path.join(self.sandbox_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            self.executed_mutations.append(f"FILE_DELETE:{filename}")
            return f"SUCCESS: Deleted file {filename}"
        return f"ERROR: File {filename} not found"

    def trigger_cloud_webhook(self, endpoint: str) -> str:
        """Triggers an external cloud registration webhook via HTTP.
        
        Args:
            endpoint: The full URL endpoint (e.g. 'https://api.cloud/register').
        """
        self.executed_mutations.append(f"WEBHOOK:{endpoint}")
        return f"SUCCESS: Webhook triggered for {endpoint}"

    # --- METRIC CALCULATION ENGINE ---

    def calculate_spi(self) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        active_db_rows = cursor.fetchone()[0]
        conn.close()

        files = [f for f in os.listdir(self.sandbox_dir) if f != "environment.db"]
        dirty_resources = active_db_rows + len(files)
        total_creations = sum(1 for m in self.executed_mutations if "CREATE" in m)

        spi = 0.0 if total_creations == 0 else min(1.0, dirty_resources / total_creations)

        return {
            "spi": spi,
            "dirty_db_rows": active_db_rows,
            "dirty_files": len(files),
            "is_clean_s0": dirty_resources == 0,
            "mutation_history": self.executed_mutations
        }