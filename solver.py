import json
from typing import List, Tuple, Dict, Set
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed

Position = Tuple[int, int]
WordResult = Dict[str, List[Position]]
SOLVER_NUMWORDS_LIMIT = 30

def get_neighbors(row: int, col: int, num_rows=4, num_cols=4) -> List[Position]:
    return [
        (r, c)
        for dr in [-1, 0, 1]
        for dc in [-1, 0, 1]
        if (dr != 0 or dc != 0) and 0 <= (r := row + dr) < num_rows and 0 <= (c := col + dc) < num_cols
    ]

def dfs(
    row: int,
    col: int,
    board: List[List[str]],
    node: dict,
    visited: Set[Position],
    current_word: str,
    current_path: List[Position],
    results: Set[str],
    paths: Dict[str, List[Position]],
):
    letter = board[row][col]
    next_node = node.get(letter)
    if not next_node:
        return

    visited.add((row, col))
    current_word += letter
    current_path.append((row, col))

    if "$" in next_node and len(current_word) >= 3:
        results.add(current_word)
        # Store path only if word not already found
        if current_word not in paths:
            paths[current_word] = list(current_path)

    for nrow, ncol in get_neighbors(row, col):
        if (nrow, ncol) not in visited:
            dfs(nrow, ncol, board, next_node, visited, current_word, current_path, results, paths)

    visited.remove((row, col))
    current_path.pop()

def dfs_worker(args):
    row, col, board, valid_starts = args
    results = set()
    paths = {}
    dfs(row, col, board, valid_starts, set(), "", [], results, paths)
    return results, paths

def find_words(board: List[List[str]], trie: dict) -> List[WordResult]:
    results = set()
    paths = {}
    board_letters = {ch for row in board for ch in row}
    valid_starts = {ch: node for ch, node in trie.items() if ch in board_letters}

    tasks = [(row, col, board, valid_starts) for row in range(len(board)) for col in range(len(board[0]))]

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(dfs_worker, task) for task in tasks]

        for future in as_completed(futures):
            rset, pset = future.result()
            results.update(rset)
            paths.update(pset)

    return [
        {"word": word, "coordinates": paths[word], "duration": max(3, len(word)), "status": "pending"}
        for word in sorted(results, key=lambda w: (-len(w), w))
    ][:min(len(results), SOLVER_NUMWORDS_LIMIT)] # limit to top 30 results for speed, change as needed

def load_trie(filepath: str) -> dict:
    with open(filepath, "rb") as f:
        return pickle.load(f)

if __name__ == "__main__":
    board = [
        ['t', 'h', 'i', 's'],
        ['w', 'a', 't', 's'],
        ['o', 'a', 'h', 'g'],
        ['f', 'g', 'd', 't']
    ]

    trie = load_trie("./trie.pkl")

    import time
    start = time.perf_counter()
    results = find_words(board, trie)
    end = time.perf_counter()

    print(f"Found {len(results)} words in {end - start:.4f} seconds")
    print(results[:10])
