from repositories.sales_report_repository import SalesReportRepository
from algorithms.greedy import sort_by_highest_profit


def generate_sales_report(mysql, start_date, end_date, branch_id=None):
    """
    Genera reporte de ventas aplicando algoritmo voraz:
    ordenado por mayor ganancia.
    """

    repo = SalesReportRepository(mysql)

    # 1. Obtener datos desde BD
    sales_data = repo.get_sales_report(start_date, end_date, branch_id)

    # 2. Aplicar algoritmo voraz
    sorted_data = sort_by_highest_profit(sales_data)

    return sorted_data
