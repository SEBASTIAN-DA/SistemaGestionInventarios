class TableService:
    def __init__(self, table_repo):
        self.table_repo = table_repo

    def get_all_tables(self, branch_id=None):
        return self.table_repo.list_tables(branch_id)

    def take_table(self, table_id, waiter_id):
        table = self.table_repo.get_table_by_id(table_id)
        if not table:
            raise ValueError("Table not found")

        if table.get('status') == 'occupied':
            return {"message": "Table already occupied", "table_id": table_id}

        self.table_repo.update_table_status(table_id, 'occupied')
        return {"message": "Table successfully occupied", "table_id": table_id}

    def release_table(self, table_id):
        table = self.table_repo.get_table_by_id(table_id)
        if not table:
            raise ValueError("Table not found")

        if table.get('status') == 'available':
            return {"message": "Table already available", "table_id": table_id}

        self.table_repo.update_table_status(table_id, 'available')
        return {"message": "Table successfully released", "table_id": table_id}
