def knapsack(products, budget):
    """
    products = [{ "name": "Cerveza", "price": 8000, "value": 9 }, ...]
    budget = dinero máximo

    Retorna lista de productos óptimos
    """

    n = len(products)
    dp = [[0 for _ in range(budget + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(budget + 1):
            if products[i-1]["price"] <= w:
                dp[i][w] = max(
                    products[i-1]["value"] + dp[i-1][w - products[i-1]["price"]],
                    dp[i-1][w]
                )
            else:
                dp[i][w] = dp[i-1][w]

    result = []
    w = budget

    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            result.append(products[i-1])
            w -= products[i-1]["price"]

    return result
