from repositories.branch_repository import fetch_all_branches

def get_all_branches():
    try:
        branches = fetch_all_branches()
        return branches
    except Exception as e:
        print("Error en branch_service:", str(e))
        return None
