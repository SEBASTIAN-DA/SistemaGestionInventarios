class TableService:
    def __init__(self, table_repo):
        self.table_repo = table_repo

    def get_all_tables(self, branch_id=None):
        return self.table_repo.list_tables(branch_id)

    # ✅ VORAZ: seleccionar la mesa óptima
    def assign_table_greedy(self, number_of_people, branch_id=None):
        """
        Algoritmo voraz:
        - Selecciona la mesa disponible más pequeña
          que soporte el número de personas.
        """

        available_tables = self.table_repo.get_available_tables(branch_id)

        if not available_tables:
            raise ValueError("No hay mesas disponibles")

        for table in available_tables:
            if table['capacity'] >= number_of_people:
                # reservar mesa
                self.table_repo.update_table_status(table['id'], 'occupied')
                return {
                    "assigned_table": table,
                    "message": "Mesa asignada con algoritmo voraz"
                }

        raise ValueError("No existe una mesa disponible para ese número de personas")

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
