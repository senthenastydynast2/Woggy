#Functions that are mostly set in stone - usually these remain untouched.
import json, random, re, datetime, os
from io import BytesIO
from tkinter import messagebox
import constants
from constants import DICTIONARY_FILE, SCRAPING_DOG_URL, LENGTH_MULTIPLIERS
from PIL import Image
import requests


def search_image(query): #For WTF function - completely optional!
    params = {
        "api_key": "680e2873fe5dbf0645187197", # Please remove me before making the game public!
        "query": query,
        "results": 5,
        "country": "us",
        "page": 0
    }
    resp = requests.get(SCRAPING_DOG_URL, params=params, timeout=5)
    if resp.status_code != 200:
        return None

    data = resp.json()
    results = data.get("images_results") or []
    if not results:
        return None

    # try each candidate, skipping ones that fail (e.g., 403s)
    for result in results:
        img_url = result.get("original") or result.get("image")
        if not img_url:
            continue
        try:
            img_resp = requests.get(img_url, timeout=5)
            img_resp.raise_for_status()
            # try opening/resizing; catch *any* error
            img = Image.open(BytesIO(img_resp.content))
            max_side = max(img.size)
            if max_side > 640:
                scale = 640 / max_side
                new_size = (int(img.width * scale), int(img.height * scale))
                img = img.resize(new_size, Image.LANCZOS)
            bio = BytesIO()
            img.save(bio, format="PNG")
            return bio.getvalue()
        except Exception:
            # network, format, PIL errors—skip to next candidate
            continue

    # none of the candidates worked
    return None

    # download the image
    img_resp = requests.get(img_url, timeout=5)
    img_resp.raise_for_status()

    # resize with Pillow if needed
    img = Image.open(BytesIO(img_resp.content))
    max_side = max(img.size)
    if max_side > 640:
        scale = 640 / max_side
        new_size = (int(img.width * scale), int(img.height * scale))
        img = img.resize(new_size, Image.LANCZOS)

    # convert to a PhotoImage
    bio = BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()



def show_def(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        txt = self.listbox.get(sel[0])
        d = self.defs.get(txt, "")
        if "=" in d:
            m = re.search(r'([A-Za-z0-9]+)=', d)
            if m:
                alias = m.group(1).upper()
                d = self.controller.dictionary.get(alias, d)
        messagebox.showinfo


def load_dictionary():
    word_dict = {}
    try:
        with open(DICTIONARY_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(None, 1)
                word = parts[0].upper()
                definition = parts[1] if len(parts) > 1 else ""
                word_dict[word] = definition
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load dictionary: {e}")
    return word_dict


def generate_random_board():
    pool = []
    for letter, prob in constants.LETTER_PROBABILITIES.items():
        pool.extend([letter] * prob)
    return [[random.choice(pool) for _ in range(4)] for _ in range(4)]


def compute_word_score(word):
    w = word.upper()
    if len(w) < 3:
        return 0
    # Tokenize based on available letter values (handles digraphs)
    tokens = []
    keys = sorted(constants.LETTER_VALUES.keys(), key=len, reverse=True)
    i = 0
    while i < len(w):
        for k in keys:
            if w.startswith(k, i):
                tokens.append(k)
                i += len(k)
                break
        else:
            tokens.append(w[i])
            i += 1
    base = sum(constants.LETTER_VALUES.get(tok, 0) * 10 for tok in tokens)
    count = len(tokens)
    if count >= 12:
        mul = 30
    else:
        mul = LENGTH_MULTIPLIERS.get(count, 1)
    return int(base * mul)


def is_word_on_board(word, board):
    w = word.upper()
    # dynamic board dimensions
    R, C = len(board), len(board[0])
    # DFS checking tiles, supports multicharacter tiles
    def dfs(r, c, idx, visited):
        tile = board[r][c]
        L = len(tile)
        # match next segment
        if w[idx:idx+L] != tile:
            return False
        idx += L
        if idx == len(w):
            return True
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < R and 0 <= nc < C and (nr, nc) not in visited:
                    if dfs(nr, nc, idx, visited | {(nr, nc)}):
                        return True
        return False
    # try starting from every tile
    for r in range(R):
        for c in range(C):
            if dfs(r, c, 0, {(r, c)}):
                return True
    # no match found
    return False


def build_prefix_set(words):
    prefixes = set()
    for w in words:
        for i in range(1, len(w) + 1):
            prefixes.add(w[:i])
    return prefixes


def find_all_words(board, dictionary, prefixes, min_len=3):
    R = C = 4
    found = set()
    def dfs(r, c, prefix, visited):
        p = prefix + board[r][c]
        if p not in prefixes:
            return
        if len(p) >= min_len and p in dictionary:
            found.add(p)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < R and 0 <= nc < C and (nr, nc) not in visited:
                    dfs(nr, nc, p, visited | {(nr, nc)})
    for r in range(R):
        for c in range(C):
            dfs(r, c, "", {(r, c)})
    return found