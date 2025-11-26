
def solve_hanoi(n, from_peg="A", to_peg="C", aux_peg="B"):
    """
    Algoritmo recursivo de Torres de Hanoi.
    Devuelve la lista de movimientos necesarios para pasar n discos
    desde from_peg hasta to_peg usando aux_peg como auxiliar.
    """
    moves = []

    def _hanoi(k, origen, destino, auxiliar):
        if k == 1:
            moves.append(f"Mover disco 1 de {origen} a {destino}")
            return
        _hanoi(k - 1, origen, auxiliar, destino)
        moves.append(f"Mover disco {k} de {origen} a {destino}")
        _hanoi(k - 1, auxiliar, destino, origen)

    _hanoi(n, from_peg, to_peg, aux_peg)
    return moves