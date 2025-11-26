def greedy_assign_table(available_tables, people_count):
    """
    Selecciona la mesa más adecuada usando algoritmo voraz.
    Prioriza la mesa con menor desperdicio de espacio.
    
    available_tables: lista de mesas [{"id":1,"capacity":4}, ...]
    people_count: personas que llegan
    """

    best_table = None
    smallest_waste = float("inf")

    for table in available_tables:
        capacity = table['capacity']

        if capacity >= people_count:
            waste = capacity - people_count

            if waste < smallest_waste:
                smallest_waste = waste
                best_table = table

    return best_table

def sort_by_highest_profit(sales_data):
    """
    Algoritmo voraz para ordenar productos por mayor ganancia.

    Regla:
    Siempre selecciona primero el registro con mayor ganancia.

    sales_data: lista de diccionarios con la clave 'ganancia'
    retorno: lista ordenada de mayor a menor ganancia
    """

    sorted_list = []
    remaining = sales_data.copy()

    while remaining:
        best = remaining[0]

        for item in remaining:
            if item['ganancia'] > best['ganancia']:
                best = item

        sorted_list.append(best)
        remaining.remove(best)

    return sorted_list
