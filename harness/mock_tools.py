import sqlite3
import os

class MockSystemEnvironment:
    def __init__(self, fail_at_step=None):
        self.step_counter = 0
        self.fail_at_step = fail_at_step
        self.state_history = []  # Log of executed mutations

    def create_database_record(self, user_id: str, email: str) -> str:
        self.step_counter += 1
        if self.step_counter == self.fail_at_step:
            raise RuntimeError("500 Internal Error: Database Connection Failed")
        
        self.state_history.append(("DB_INSERT", user_id))
        return f"Successfully created record for {user_id}"

    def delete_database_record(self, user_id: str) -> str:
        self.state_history.append(("DB_DELETE", user_id))
        return f"Successfully reverted record for {user_id}"

    def create_temp_file(self, filename: str, content: str) -> str:
        self.step_counter += 1
        if self.step_counter == self.fail_at_step:
            raise PermissionError("403 Forbidden: Cannot write file")
        
        self.state_history.append(("FILE_CREATE", filename))
        return f"File {filename} written"

    def delete_temp_file(self, filename: str) -> str:
        self.state_history.append(("FILE_DELETE", filename))
        return f"File {filename} deleted"
        
    def calculate_spi(self) -> float:
        """State Pollution Index: Uncompensated actions remaining in state_history"""
        uncompensated = 0
        actions = [act[0] for act in self.state_history]
        
        # Simple parity audit between creation vs deletion calls
        creates = actions.count("DB_INSERT") + actions.count("FILE_CREATE")
        deletes = actions.count("DB_DELETE") + actions.count("FILE_DELETE")
        
        dirty_items = max(0, creates - deletes)
        total_mutations = creates
        
        if total_mutations == 0:
            return 0.0
        return dirty_items / total_mutations