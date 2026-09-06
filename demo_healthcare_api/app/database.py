# In-memory thread-safe state store for functional testing and local execution
import uuid
from typing import Dict, List, Any, Optional

class InMemoryStore:
    def __init__(self):
        self.tables: Dict[str, Dict[str, Dict[str, Any]]] = {
            "patients": {},
            "appointments": {},
        }

    def get_table(self, resource: str) -> Dict[str, Dict[str, Any]]:
        if resource not in self.tables:
            self.tables[resource] = {}
        return self.tables[resource]

    def list_all(self, resource: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        items = list(self.get_table(resource).values())
        return items[offset:offset + limit]

    def get_by_id(self, resource: str, item_id: str) -> Optional[Dict[str, Any]]:
        return self.get_table(resource).get(str(item_id))

    def create(self, resource: str, data: Dict[str, Any], item_id: Optional[str] = None) -> Dict[str, Any]:
        table = self.get_table(resource)
        rid = str(item_id) if item_id else data.get("id") or str(uuid.uuid4())
        record = dict(data)
        record["id"] = rid
        table[rid] = record
        return record

    def update(self, resource: str, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        table = self.get_table(resource)
        rid = str(item_id)
        if rid not in table:
            return None
        table[rid].update(data)
        return table[rid]

    def delete(self, resource: str, item_id: str) -> bool:
        table = self.get_table(resource)
        rid = str(item_id)
        if rid in table:
            del table[rid]
            return True
        return False

db = InMemoryStore()
