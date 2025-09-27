import json
import re

from typing import List, Tuple, Dict, Set

Position = Tuple[int, int]
WordResult = Dict[str, List[Position]]


def get_neighbors(row: int, col: int, num_rows=4, num_cols=4) -> List[Position]:
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if 0 <= r < num_rows and 0 <= c < num_cols:
                neighbors.append((r, c))
    return neighbors


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
    next_node = node.get("children", {}).get(letter)

    if not next_node:
        return

    visited.add((row, col))
    current_word += letter
    current_path.append((row, col))

    if next_node.get("isEndOfWord") and len(current_word) >= 3:
        results.add(current_word)
        paths[current_word] = list(current_path)

    for nrow, ncol in get_neighbors(row, col):
        if (nrow, ncol) not in visited:
            dfs(nrow, ncol, board, next_node, visited, current_word, current_path, results, paths)

    visited.remove((row, col))
    current_path.pop()


def find_words(board: List[List[str]], trie: dict) -> List[WordResult]:
    results = set()
    paths = {}

    for row in range(4):
        for col in range(4):
            dfs(
                row, col,
                board,
                trie,
                visited=set(),
                current_word="",
                current_path=[],
                results=results,
                paths=paths
            )

    return [
        {"word": word, "path": paths[word]}
        for word in sorted(results, key=lambda w: (-len(w), w))
    ]


def load_trie_from_js(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    json_str = re.sub(r'^export\s+const\s+\w+\s+=\s+', '', content).rstrip('; \n')
    return json.loads(json_str)

board = [
    ['t', 'h', 'i', 's'],
    ['w', 'a', 't', 's'],
    ['o', 'a', 'h', 'g'],
    ['f', 'g', 'd', 't']
]

trie = load_trie_from_js("/home/memryx/Documents/repos/trie.js")

# Get all possible words and paths
results = find_words(board, trie)