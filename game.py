import tkinter as tk
import time
from tkinter import ttk, messagebox
from operator import itemgetter
import os, string, json, datetime, re
from io import BytesIO
from PIL import Image, ImageTk
import random

from constants import (
    LETTER_PROBABILITIES_ENGLISH,
    LETTER_VALUES_ENGLISH,
    LETTER_PROBABILITIES_SPANISH,
    LETTER_VALUES_SPANISH,
    LENGTH_MULTIPLIERS,
    SETTINGS_FOLDER,
    SETTINGS_FILE,
    TILES_FOLDER,
    BADGES_FOLDER,
    TIMER_MAP,
    BOARD_BG_COLORS,
    CLASSIFICATION_THRESHOLDS,
    BOARD_HANDICAP_MAP,
    get_rank_from_ratio,
    get_rank_info,
    get_wordhogger_threshold
)
from utils import (
    load_dictionary,
    build_prefix_set,
    generate_random_board,
    compute_word_score,
    is_word_on_board,
    find_all_words,
    search_image
)

class WoggyGame(tk.Tk):
    def blend_color(self, color_name, white_pct):
        # blend a named color with white by white_pct (0-1)
        r, g, b = self.winfo_rgb(color_name)
        # tkinter gives 16-bit RGB
        r = int(r/256); g = int(g/256); b = int(b/256)
        # white is (255,255,255)
        nr = int(r*(1-white_pct) + 255*white_pct)
        ng = int(g*(1-white_pct) + 255*white_pct)
        nb = int(b*(1-white_pct) + 255*white_pct)
        return f"#{nr:02x}{ng:02x}{nb:02x}"
    def __init__(self):
        super().__init__()
        self.configure(bg="#fefbf9")
        self._base_w, self._base_h = 720, 920
        self._menu_w, self._menu_h = self._base_w + 200, self._base_h // 2
        os.makedirs(SETTINGS_FOLDER, exist_ok=True)
        self.settings = {}
        self.load_settings()
        self.title("Woggy")
        self.resizable(True, True)
        self.geometry(f"{self._menu_w}x{self._menu_h}")
        self.center_window(self._menu_w, self._menu_h)
        self.dictionary = load_dictionary()
        self.prefixes = build_prefix_set(self.dictionary.keys())
        self.letter_images = {}
        self.load_letter_images()
        self.load_badge_images()
        self.entered_words = []
        self.judged_words = []  # track ?-queries
        self.board = None
        self.time_remaining = 0
        self.total_score = 0
        self.potential_score = 0
        self.board_potential = 0    
        # default to whatever was last saved
        self.selected_language = tk.StringVar(
            value=self.settings.get('last_language', 'English')
        )
        self.selected_mode     = tk.StringVar(
            value=self.settings.get('last_mode', 'Standard')
        )        
        # Apply language settings before loading resources
        self.apply_language_settings()
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        #NEW - Self-Contained Grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (MainMenu, SubMenu, GameScreen, EndScreen, SummaryScreen):
            page = F(container, self)
            self.frames[F.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")
        self.show_frame("MainMenu")

    def center_window(self, w, h):
        self.update_idletasks()
        ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (ws - w)//2, (hs - h)//2
        self.geometry(f"{w}x{h}+{x}+{y}")
        
    def start_quick_play(self):
        self.subtype = "quick_play"
        self.start_game()

    def start_world_tour(self):
        self.subtype = "world_tour"
        # prepare 10 specific board potentials for WT
        self.world_tour_rounds = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
        random.shuffle(self.world_tour_rounds)
        self.world_tour_data = []
        self.current_round_index = 0
        self.start_next_world_round()
        
    def start_next_world_round(self):
        # clear previous round’s Word-Judge queries
        self.judged_words.clear()

        # pick the next target potential
        pot = self.world_tour_rounds[self.current_round_index]

        # show generation popup (modal & centered)
        loading = tk.Toplevel(self)
        loading.title("")
        loading.resizable(False, False)
        loading.transient(self)
        loading.grab_set()  # prevent manual close
        # display message
        msg = tk.Label(
            loading,
            text="Please wait. Board generation speeds take longer on slower systems...",
            padx=20,
            pady=10
        )
        msg.pack()
        # draw immediately so label is visible and we can measure size
        loading.update()
        w, h = loading.winfo_width(), loading.winfo_height()
        # center on screen
        sw = loading.winfo_screenwidth()
        sh = loading.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        loading.geometry(f"{w}x{h}+{x}+{y}")
        # ensure rendering before delay
        loading.update()
        # brief pause
        time.sleep(1)

        # generate boards until one matches the desired potential
        while True:
            board = generate_random_board()
            words = find_all_words(board, self.dictionary, self.prefixes)
            score_sum = sum(compute_word_score(w) for w in words)
            _, _, val = self.classification_for(score_sum)
            if val == pot:
                break

        # dismiss the popup
        loading.destroy()

        # set up this round
        self.board = board
        self.potential_score = score_sum
        # compute and store classification
        _, _, bpv = self.classification_for(self.potential_score)
        self.board_potential = bpv
        # use the fixed 'pot' value for threshold, not the derived bpv
        self.wh_remaining = get_wordhogger_threshold(pot)
        self.hw_remaining = 5 #Reset the Heavyweight counter for World Tour
        # do NOT show the counter yet—start_round() will handle that

        # start the timer and game
        self.time_remaining = TIMER_MAP[bpv]
        self.frames['GameScreen'].initialize_game()
        self.show_frame('GameScreen')


    def next_round(self):
         self.current_round_index += 1
         if self.current_round_index < len(self.world_tour_rounds):
             self.start_next_world_round()
         else:
             self.show_summary()

    def show_summary(self):
        # 1) aggregate scores and ratios
        total_score = sum(r['score'] for r in self.world_tour_data)
        avg_rs = sum(r['rs'] for r in self.world_tour_data) / len(self.world_tour_data)
        # 2) compute final rank letter
        final_rank, _, _ = get_rank_info(avg_rs)
        # 3) tally badges
        badge_totals = {}
        for rd in self.world_tour_data:
            for k, v in rd['badges'].items():
                badge_totals[k] = badge_totals.get(k, 0) + v
        # 4) find overall best word
        best_round = max(self.world_tour_data, key=lambda r: r['highest_word_score'])
        best_word = best_round['highest_word']
        best_score = best_round['highest_word_score']
        # 5) write summary to a .txt
        fname = os.path.join("Scores", f"worldtour_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt")
        with open(fname, 'w') as f:
            f.write(f"World Tour Complete!\n\n")
            f.write(f"Total Score: {total_score}\n")
            f.write(f"Average RS: {avg_rs:.2f}\n")
            f.write(f"Final Rank: {final_rank}\n\n")
            f.write("Badges Earned:\n")
            for k, v in badge_totals.items():
                f.write(f" - {k}: x{v}\n")
            f.write(f"\nTop Word Overall: {best_word} ({best_score} pts)\n")
        # 6) display SummaryScreen
        screen = self.frames['SummaryScreen']
        screen.display(
            total_score=total_score,
            avg_rs=avg_rs,
            final_rank=final_rank,
            badge_totals=badge_totals,
            best_word=best_word,
            best_score=best_score,
            summary_file=fname
        )
        self.show_frame('SummaryScreen')

    def load_settings(self):
        try:
            with open(SETTINGS_FILE) as f:
                self.settings = json.load(f)
        except:
            self.settings = {'tile_size': 150, 'judge': True}
        self.settings.setdefault('tile_size', 150)
        self.settings.setdefault('judge', True)
        
    def apply_language_settings(self):
        import constants
        lang = self.selected_language.get()
        if lang == 'Spanish':
            constants.LETTER_PROBABILITIES = constants.LETTER_PROBABILITIES_SPANISH
            constants.LETTER_VALUES = constants.LETTER_VALUES_SPANISH
            constants.DICTIONARY_FILE = constants.DICTIONARY_FILE_SPANISH
            constants.TILES_FOLDER = constants.TILES_FOLDER_SPANISH
        else:
            constants.LETTER_PROBABILITIES = constants.LETTER_PROBABILITIES_ENGLISH
            constants.LETTER_VALUES = constants.LETTER_VALUES_ENGLISH
            constants.DICTIONARY_FILE = constants.DICTIONARY_FILE_ENGLISH
            constants.TILES_FOLDER = constants.TILES_FOLDER_ENGLISH

    

    def save_settings(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f)

    def load_letter_images(self):
        size = self.settings.get('tile_size', 150)
        for l in string.ascii_uppercase:
            path = os.path.join(TILES_FOLDER, f"{l}.png")
            if os.path.exists(path):
                img = tk.PhotoImage(file=path)
                if size != 150:
                    factor = max(1, int(150/size))
                    img = img.subsample(factor, factor)
                self.letter_images[l] = img
            else:
                self.letter_images[l] = None
        blank_path = os.path.join(TILES_FOLDER, 'blank.png')
        if os.path.exists(blank_path):
            bimg = tk.PhotoImage(file=blank_path)
            if size != 150:
                factor = max(1, int(150/size))
                bimg = bimg.subsample(factor, factor)
            self.blank_image = bimg

    def load_badge_images(self):
        # shrink each badge image by 10px
        self.badge_images = {}
        # include both “off” and “on” versions of our Word Hogger badge
        for name in ('homerun','eagleeye','wordhogger','wordhogger_off','wordhogger_on','erudite','pottymouth', 'heavyweight', 'heavyweight_on', 'heavyweight_off'):
            path = os.path.join(BADGES_FOLDER, f"{name}.png")
            if os.path.exists(path):
                pil_img = Image.open(path)
                w, h = pil_img.size
                new_size = (max(1, w - 10), max(1, h - 10))
                pil_img = pil_img.resize(new_size, Image.LANCZOS)
               # first shrink by 10px in each dimension
                new_size = (max(1, w - 10), max(1, h - 10))
                pil_img = pil_img.resize(new_size, Image.LANCZOS)
                # Resize only for the small counter icons
                if name in ('wordhogger_off', 'wordhogger_on', 'heavyweight_off', 'heavyweight_on'):
                    w, h = pil_img.size
                    new_size = (max(1, w // 2), max(1, h // 2))
                    pil_img = pil_img.resize(new_size, Image.LANCZOS)
                # Convert to Tk image and store
                tk_img = ImageTk.PhotoImage(pil_img)
                self.badge_images[name] = tk_img
                             
        # reload the real blank-tile graphic so pause/countdown shows it
        blank_path = os.path.join(TILES_FOLDER, 'blank.png')
        if os.path.exists(blank_path):
            self.blank_image = tk.PhotoImage(file=blank_path)

    def open_settings(self):
        win = tk.Toplevel(self)
        win.title("Options")
        win.grab_set()
        # Tile‐size slider: 15–150 px, 1 px increments
        tk.Label(win, text="Tile Size (Default is 79):").pack(pady=5)
        ts_var = tk.IntVar(value=self.settings['tile_size'])
        slider = tk.Scale(
            win,
            from_=15,
            to=150,
            orient='horizontal',
            variable=ts_var,
            length=300
        )
        slider.pack(pady=5)
        # Rank‐popup toggle
        jv = tk.BooleanVar(value=self.settings['judge'])
        tk.Checkbutton(win, text="Show Rank Popups", variable=jv).pack(pady=5)
        # Save/Cancel
        frm = tk.Frame(win)
        frm.pack(pady=10)
        def on_save():
            self.settings['tile_size'] = ts_var.get()
            self.settings['judge'] = jv.get()
            self.save_settings()
            self.load_letter_images()
            win.destroy()
        tk.Button(frm, text="Save", command=on_save).pack(side='left', padx=5)
        tk.Button(frm, text="Cancel", command=win.destroy).pack(side='left', padx=5)

    def show_frame(self, name):
        page = self.frames[name]
        page.tkraise()
        if name == "MainMenu":
            self.geometry(f"{self._menu_w}x{self._menu_h}")
            self.center_window(self._menu_w, self._menu_h)
        elif name == "SubMenu":
            # make SubMenu much shorter (~35% of default height)
            w, h = self._base_w, int(self._base_h * 0.35)
            ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
            x = (ws - w) // 2
            y = (hs - h) // 2
            self.geometry(f"{w}x{h}+{x}+{y}")
        else:
            # gameplay screens sit 75px above perfect center
            w, h = self._base_w, self._base_h
            ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
            x = (ws - w) // 2
            y = (hs - h) // 2 - 75
            self.geometry(f"{w}x{h}+{x}+{y}")

    def start_game(self):
        self.entered_words.clear()
        self.judged_words.clear()
        self.total_score = 0
        self.board = generate_random_board()
        all_words = find_all_words(self.board, self.dictionary, self.prefixes)
        all_scores = {w: compute_word_score(w) for w in all_words}
        self.potential_score = sum(all_scores.values())
        msg, color, bpv = self.classification_for(self.potential_score)
        self.board_potential = bpv
        # set up the Word-Hogger “remaining words” counter
        self.wh_remaining = get_wordhogger_threshold(self.board_potential)
        # set up Heavyweight counter (starts at 5 as of now)
        self.hw_remaining = 5
        # tell GameScreen to draw it
        self.frames['GameScreen'].update_wordhogger_counter()
        self.frames['GameScreen'].update_heavyweight_counter()
        self.time_remaining = TIMER_MAP[bpv]
        self.frames['GameScreen'].initialize_game()
        # store these choices for next time
        self.settings['last_language'] = self.selected_language.get()
        self.settings['last_mode']     = self.selected_mode.get()
        self.save_settings()
        self.show_frame('GameScreen')

    def end_game(self):
        user_valid, user_scores = [], {}
        #check for WT mode
        is_world = getattr(self, 'subtype', '') == 'world_tour'
        user_valid, user_scores = [], {}
        incorrect = []
        for w in set(self.entered_words):
            uw = w.upper().strip()
            if len(uw) < 3:
                continue
            on_board = is_word_on_board(uw, self.board)
            if on_board:
                if uw in self.dictionary:
                    sc = compute_word_score(uw)
                    user_valid.append(uw)
                    user_scores[uw] = sc
                else:
                    # penalty: half of theoretical score
                    penal = compute_word_score(uw) // 2
                    incorrect.append((uw, penal))
            # words not on board are ignored entirely
        base_score = sum(user_scores.values())
        # apply penalties
        for _, penal in incorrect:
            base_score -= penal
        all_words = find_all_words(self.board, self.dictionary, self.prefixes)
        all_scores = {w: compute_word_score(w) for w in all_words}
        self.potential_score = sum(all_scores.values())
        bonuses = []
        if all_words:
            max_sc = max(all_scores.values())
            if any(sc == max_sc for sc in user_scores.values()):
                bonuses.append("Homerun | 5% Bonus!")
            max_len = max(len(w) for w in all_words)
            if any(len(w) == max_len for w in user_valid):
                bonuses.append("Eagle Eye | 5% Bonus!")
        # Word Hogger threshold for this board
        thresh = get_wordhogger_threshold(self.board_potential)
        if thresh>0 and len(user_valid)>=thresh:
            bonuses.append("Word Hogger | 5% Bonus!")
        # Hardcore Erudite badge 
        if self.selected_mode.get().strip().lower()=="hardcore":
            if not incorrect:
                bonuses.append("Erudite | 15% Bonus!")
        #Count Pottymouth Words
        pottymouth_count = sum(1 for w in user_valid if "an offensive word" in self.dictionary.get(w, "").lower())
        if pottymouth_count >= 3:
            bonuses.append("Pottymouth | 5% Bonus!")        
        # Heavyweight badge: 7 or more valid words of length ≥7
        heavyweight_count = sum(1 for w in user_valid if len(w) >= 7)
        if heavyweight_count >= 5:
            bonuses.append("Heavyweight | 5% Bonus!")    
        # Apply badge bonuses
        final = base_score
        for b in bonuses:
            if b.startswith("Erudite"):
                factor = 1.15
            elif b.startswith("Pottymouth"):
                factor = 1.05
            else:
                factor = 1.05
            final = int(final * factor)
        # Apply board type handicap as flat score adjustment
        bpv = self.board_potential
        handicap_pct = BOARD_HANDICAP_MAP.get(bpv, 0)
        if handicap_pct != 0:
            adj = int(final * handicap_pct / 100)
            final += adj
            self.handicap_note = f"{handicap_pct:+.0f}% board type handicap"
        else:
            self.handicap_note = None    
        self.last_bonuses = bonuses
        self.total_score = final        
        if bonuses:
            messagebox.showinfo("Bonuses Earned!", "\n".join(bonuses))
        if self.settings.get('judge', True):
            if self.potential_score > 0:
                # Long Word Handicap: Ignore score of 10+ letter words, half-score for 8-9 letters
                deductions = 0
                for w, sc in all_scores.items():
                    lw = len(w)
                    if lw >= 10:
                        deductions += sc
                    elif lw in (8, 9):
                        deductions += sc * 0.5
                adjusted_ps = max(1, self.potential_score - deductions)
                rs = int((self.total_score / adjusted_ps) * 100) / 100.0
            else:
                rs = 0.0
            # ensure rs does not exceed 1.0
            rs = min(rs, 1.0)
            rk, rc, msg = get_rank_info(rs)
            messagebox.showinfo("Your Rank", msg)
            self.frames['EndScreen'].draw_rank(rk, rc)
        self.save_session(user_valid, user_scores, base_score, self.potential_score, bonuses)
        # store incorrect words for popup (don’t show them in the main list)
        self.incorrect_words = [w for w, _ in incorrect]
        # now display the normal results (incorrect words removed from here)
        self.frames['EndScreen'].display_results(
            user_valid, user_scores, all_words, all_scores,
            self.dictionary, self.potential_score,
            incorrect, self.selected_mode.get()
        )
        self.show_frame('EndScreen')
        # if in world tour, capture this round and set up “Next Round”
        if is_world:
            # best word
            if user_scores:
                hw, hw_score = max(user_scores.items(), key=itemgetter(1))
            else:
                hw, hw_score = '', 0
            # count badges
            badge_keys = ['Homerun', 'Eagle Eye', 'Word Hogger', 'Erudite', 'Pottymouth', 'Heavyweight']
            counts = {k: sum(1 for b in self.last_bonuses if b.startswith(k)) for k in badge_keys}
            # rs ratio
            rs = int((self.total_score / self.potential_score) * 100) / 100.0 if self.potential_score else 0
            # store this round's data
            self.world_tour_data.append({
                'round': self.current_round_index + 1,
                'score': self.total_score,
                'highest_word': hw,
                'highest_word_score': hw_score,
                'badges': counts,
                'rs': rs
            })
            # tweak EndScreen
            es = self.frames['EndScreen']
            es.header_label.config(
                text=f"Round {self.current_round_index+1}/{len(self.world_tour_rounds)}"
            )
            # Next Round must still go through our _on_end_button wrapper
            # round numbers go 1–12; when we’ve just finished round 12, show “See Results”
            if self.current_round_index == len(self.world_tour_rounds) - 1:
                es.play_again_btn.config(text="See Results", command=self.show_summary)
            else:
                es.play_again_btn.config(text="Next Round", command=self.next_round)
            return

    def classification_for(self, ps):
        for thresh, label, color, val in CLASSIFICATION_THRESHOLDS:
            if ps <= thresh:
                return label, color, val

    def save_session(self, uv, us, bs, ps, bonuses):
        now = datetime.datetime.now()
        folder = "Scores"
        os.makedirs(folder, exist_ok=True)
        fn = os.path.join(folder, f"session_{self.total_score}_{now.strftime('%Y%m%d_%H%M%S')}.txt")
        with open(fn, 'w') as f:
            f.write(f"Total Score: {self.total_score}\nPossible Score: {ps}\n")
            if self.handicap_note:
                f.write(f"{self.handicap_note}\n")
            f.write("Bonuses:\n")
            for b in bonuses or []:
                f.write(f"- {b}\n")
            f.write("Board:\n")
            for row in self.board:
                f.write("-".join(row)+"\n")
            f.write("Found Words:\n")
            for w in sorted(uv, key=lambda x: us[x], reverse=True):
                f.write(f"{w}\t{us[w]}\t{self.dictionary.get(w,"")}\n")

    def rotate_board(self):
        if self.board:
            # rotate board 90° clockwise
            self.board = [list(r) for r in zip(*self.board[::-1])]
            # refresh GameScreen display without resetting timer or state
            gs = self.frames.get('GameScreen')
            if gs and hasattr(gs, 'draw_board'):
                gs.draw_board()

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        inner = tk.Frame(self)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        self.controller = controller
        self.grid(sticky="nsew")
        # Title splash image instead of text
        splash_path = os.path.join(BADGES_FOLDER, "splash.png")
        try:
            img = Image.open(splash_path)
            # resize to exactly 600×100 (change to your desired width/height)
            img = img.resize((300, 80), Image.LANCZOS)
            self.splash_img = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.splash_img, bd=0, relief='flat', highlightthickness=0).pack(pady=5)
        except Exception:
            # fallback if splash.png is missing or fails to load
            tk.Label(self, text="Woggy", font=("Helvetica", 42, "bold")).pack(pady=5)
        tk.Label(self, text="Select Language:").pack(pady=5)
        ttk.Combobox(
            self,
            textvariable=controller.selected_language,
            values=["English", "Coming Soon!"]
        ).pack(pady=5)
        #tk.Label(inner, text="Select Game Type:").pack(pady=5)
        fm = tk.Frame(inner); fm.pack(pady=5)
        tk.Radiobutton(fm, text="Standard", variable=controller.selected_mode, value="Standard").pack(side="left", padx=10)
        tk.Radiobutton(fm, text="Hardcore", variable=controller.selected_mode, value="Hardcore").pack(side="left", padx=10)        
        tk.Button(inner, text="Start Game", font=("Helvetica", 16), command=lambda: controller.show_frame("SubMenu")).pack(pady=20)        
        tk.Button(inner, text="Options", font=("Helvetica", 12), command=controller.open_settings).pack(pady=5)

class SubMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid(sticky="nsew")
        tk.Label(self, text="Choose Mode:", font=("Helvetica", 24, "bold")).pack(pady=10)
        tk.Button(self, text="Quick Play", font=("Helvetica", 16),
                  command=controller.start_quick_play).pack(pady=5)
        tk.Button(self, text="World Tour", font=("Helvetica", 16),
                  command=controller.start_world_tour).pack(pady=5)



class GameScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        inner = tk.Frame(self)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        self.controller = controller
        self.rotate_allowed = False
        self.controller.bind('<space>', self.on_space)
        self.controller.bind('<Escape>', self.toggle_pause)
        self.paused = False
        self.saved_time = 0        
        self.grid(sticky="nsew")
        self.timer_label = tk.Label(self, text="Get Ready...", font=("Helvetica", 42)) #Time Shown During Wait Screen
        self.timer_label.pack(pady=(5,0))
        # display game mode under the timer
        self.mode_label = tk.Label(self, text="", font=("Helvetica", 12, "bold italic"))
        self.mode_label.pack(pady=(2,2))
        # Word Hogger remaining‐words counter: small pig + large bold number
        self.wh_frame = tk.Frame(self, bd=0, highlightthickness=0)
        # This doesn't seem to control the position of the hog but I'm leaving it in just in case
        self.wh_frame.place(relx=0.60, rely=0.82, anchor='ne')
        # initially hidden; we’ll show it only after the WAIT screen
        self.wh_frame.place_forget()
        off_img = self.controller.badge_images.get('wordhogger_off')
        self.wh_icon = tk.Label(self.wh_frame, image=off_img, bd=0, highlightthickness=0)
        self.wh_icon.image = off_img
        self.wh_icon.pack(side='left')
        self.wh_label = tk.Label(                #Word Hogger Counter Location
            self.wh_frame,
            text='',
            font=("Helvetica", 30, "bold"),
            bd=0,
            highlightthickness=0
        )
        self.wh_label.pack(side='left', padx=(3,0))
        # Heavyweight remaining‐words counter: small icon + large bold number
        self.hw_frame = tk.Frame(self, bd=0, highlightthickness=0)
        # mirror WH placement but on left
        self.hw_frame.place(relx=0.09, rely=0.82, anchor='nw')
        self.hw_frame.place_forget()
        hw_off = self.controller.badge_images.get('heavyweight_off')
        self.hw_icon = tk.Label(self.hw_frame, image=hw_off, bd=0, highlightthickness=0)
        self.hw_icon.image = hw_off
        self.hw_icon.pack(side='left')
        self.hw_label = tk.Label(
            self.hw_frame,
            text='',
            font=("Helvetica", 30, "bold"),
            bd=0,
            highlightthickness=0
        )
        self.hw_label.pack(side='left', padx=(3,0))
        
        
        
        
        self.board_frame = tk.Frame(self)
        self.board_frame.pack(pady=(0,0)) #Padding between timer and game mode
        ef = tk.Frame(self)
        ef.pack(pady=(2,5)) #Bring Entry Up
        self.entry_var = tk.StringVar()
        self.entry_var.trace_add('write', self._on_entry)
        self.word_entry = tk.Entry(ef, font=("Helvetica", 16), textvariable=self.entry_var)
        self.word_entry.pack(side="left")
        self.word_entry.bind("<Return>", lambda e: self.submit_word())
        self.words_display = tk.Listbox(self, height=5, width=50)
        self.words_display.pack(pady=(2, 5)) # Entry Box Padding
        bf = tk.Frame(self)
        bf.pack(side="bottom", pady=5)
        tk.Button(bf, text="New Board", command=self.confirm_new).pack(side="left", padx=10)
        tk.Button(bf, text="End Early", command=self.confirm_finish).pack(side="left", padx=10)
        self.timer_id = None

    def initialize_game(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        # display “WAIT” for 3s
        self.draw_message_board("WAIT")
        self.words_display.delete(0, tk.END)
        self.entry_var.set("")
        self.after(3000, self.start_round)

    def on_space(self, event):
        # prevent rotation while paused
        if self.paused:
            return
        if self.rotate_allowed:
            self.controller.rotate_board()
            self.rotate_allowed = False
            self.after(1500, lambda: setattr(self, 'rotate_allowed', True))

    def start_round(self):
        self.word_entry.config(state='normal')
        # update mode text & color
        mode = self.controller.selected_mode.get() + " Mode"
        fg = "red" if self.controller.selected_mode.get() == "Hardcore" else "black"
        self.mode_label.config(text=mode, fg=fg)
        self.rotate_allowed = True
        self.draw_board()
        self.update_wordhogger_counter()
        # after WAIT, show both counters
        self.wh_frame.place(relx=0.91, y=40, anchor='ne')
        self.hw_frame.place(relx=0.09, y=40, anchor='nw')
        self.update_wordhogger_counter()
        self.update_heavyweight_counter()
        self.words_display.delete(0, tk.END)
        self.entry_var.set("")
        self.word_entry.focus_set()
        bpv = self.controller.board_potential
        base_color = BOARD_BG_COLORS.get(bpv, '#fefbf9')
        # For extreme boards, use a deeper color to indicate urgency/rarity
        if bpv in (1, 2, 3):
            blend_pct = 0.10
        elif bpv in (4, 5, 6, 32):
            blend_pct = 0.15
        elif bpv in (7, 8, 9, 31):
            blend_pct = 0.20
        elif bpv in (29, 30):
            blend_pct = 0.25
        else:
            blend_pct = 0.40  # default if none of the above
        color = self.controller.blend_color(base_color, blend_pct)
        def apply_bg(widget, bg):
            try:
                widget.configure(bg=bg)
            except tk.TclError:
                pass
            for child in widget.winfo_children():
                apply_bg(child, bg)
        apply_bg(self.controller, color)
        duration_ms = TIMER_MAP.get(bpv, 0) * 1000 + 3000
        if duration_ms > 0:
            self.after(duration_ms, lambda: apply_bg(self.controller, '#fefbf9'))
        self.update_timer()

    def update_timer(self):
        mins, secs = divmod(self.controller.time_remaining, 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
        if self.controller.time_remaining > 0:
            self.controller.time_remaining -= 1
            self.timer_id = self.after(1000, self.update_timer)
        else:
            # round is over — show STOP for 3 s, then proceed
            self.draw_message_board("STOP")
            self.word_entry.config(state='disabled')
            self.rotate_allowed = False
            self.after(3000, lambda: self.controller.end_game())
            
    def update_wordhogger_counter(self):
        # Refresh the pig icon (off→on) and remaining‐words count.
        rem = getattr(self.controller, 'wh_remaining', 0)
        # pick off/on graphic
        key = 'wordhogger_on' if rem <= 0 else 'wordhogger_off'
        img = self.controller.badge_images.get(key)
        if img:
            self.wh_icon.config(image=img)
            self.wh_icon.image = img
        # show or hide the number
        if rem <= 0:
            self.wh_label.config(text='')
        else:
            self.wh_label.config(text=str(rem))     

    def update_heavyweight_counter(self):
        """Refresh the heavyweight icon (off→on) and remaining‐words count."""
        rem = getattr(self.controller, 'hw_remaining', 0)
        key = 'heavyweight_on' if rem <= 0 else 'heavyweight_off'
        img = self.controller.badge_images.get(key)
        if img:
            self.hw_icon.config(image=img)
            self.hw_icon.image = img
        if rem <= 0:
            self.hw_label.config(text='')
        else:
            self.hw_label.config(text=str(rem))        

    def draw_message_board(self, msg: str):
        for w in self.board_frame.winfo_children():
            w.destroy()
        L = len(msg)
        for r in range(4):
            for c in range(4):
                # grab blank tile if available
                blank_img = getattr(self.controller, 'blank_image', None)
                if r == c and r < L:
                    # diagonal letter
                    letter = msg[r].upper()
                    img = self.controller.letter_images.get(letter)
                    if img:
                        lbl = tk.Label(self.board_frame, image=img)
                        lbl.image = img
                    else:
                        lbl = tk.Label(self.board_frame, text=letter, font=("Helvetica",48))
                else:
                    # blank tile
                    if blank_img:
                        lbl = tk.Label(self.board_frame, image=blank_img)
                        lbl.image = blank_img
                    else:
                        lbl = tk.Label(self.board_frame, text="", width=4, height=2)
                lbl.grid(row=r, column=c, padx=2, pady=2)

    def draw_blank_board(self):
        for w in self.board_frame.winfo_children():
            w.destroy()
        for r in range(4):
            for c in range(4):
                if getattr(self.controller, 'blank_image', None):
                    lbl = tk.Label(self.board_frame, image=self.controller.blank_image)
                else:
                    lbl = tk.Label(self.board_frame, text="", width=4, height=2)
                lbl.grid(row=r, column=c, padx=2, pady=2)

    def draw_board(self):
        for w in self.board_frame.winfo_children():
            w.destroy()
        board = self.controller.board
        for r in range(4):
            for c in range(4):
                l = board[r][c]
                img = self.controller.letter_images.get(l)
                if img:
                    lbl = tk.Label(self.board_frame, image=img)
                else:
                    lbl = tk.Label(self.board_frame, text=l, font=("Helvetica", 48))
                lbl.grid(row=r, column=c, padx=2, pady=2)


    def submit_word(self, event=None):
        raw = self.entry_var.get().strip()
        # Interpret ';' as 'Ñ' in Spanish mode
        raw = raw.replace(';', 'Ñ')
        # deletion request (prefix '-')
        if raw.startswith('-'):
            # remove the last submitted word if any
            if self.controller.entered_words:
                self.controller.entered_words.pop()
                try:
                    self.words_display.delete(0)
                except Exception:
                    pass
                # bump Word-Hogger counter up by 1 upon deletion
                if hasattr(self.controller, 'wh_remaining'):
                    self.controller.wh_remaining += 1
                    self.update_wordhogger_counter()
                # bump Heavyweight counter up by 1 if deleted word ≥7 letters
                target = raw[1:].upper()
                if hasattr(self.controller, 'hw_remaining') and len(target) >= 7:
                    self.controller.hw_remaining += 1
                    self.update_heavyweight_counter()
            # clear entry box and exit
            self.entry_var.set("")
            return

        # normal submission path
        word = raw.upper()
        # Heavyweight: tick down for every 7+ letter submission
        if hasattr(self.controller, 'hw_remaining') and len(word) >= 7 and not raw.startswith('?'):
            self.controller.hw_remaining = max(0, self.controller.hw_remaining - 1)
            self.update_heavyweight_counter()
        if word:
            is_new = word not in self.controller.entered_words
            self.controller.entered_words.append(word)
            if is_new and hasattr(self.controller, 'wh_remaining'):
                # leave judge-queries ('?WORD') intact
                if '?' in word:
                    self.controller.judged_words.append(word)
                else:
                    # consume one for valid new words
                    self.controller.wh_remaining = max(0, self.controller.wh_remaining - 1)
                    self.update_wordhogger_counter()
        # display in list
        self.words_display.insert(0, word)
        self.words_display.itemconfig(0, fg='black')
        self.entry_var.set("")
        self.word_entry.focus_set()
        return 

        # 2) In Hardcore only: allow removal with '-'
        if mode == "hardcore" and raw.startswith('-') and len(raw) > 1:
            target = raw[1:].upper()
            # remove all occurrences from entered_words + Listbox
            self.controller.entered_words = [w for w in self.controller.entered_words if w != target]
            for i in range(self.words_display.size()-1, -1, -1):
                if self.words_display.get(i).upper() == target:
                    self.words_display.delete(i)
            self.entry_var.set("")
            return

        # 3) Normal word entry
        word = raw.upper()
        if word:
            # only count brand-new, “real” words toward Word Hogger
            is_new = word not in self.controller.entered_words
            self.controller.entered_words.append(word)
            if is_new and hasattr(self.controller, 'wh_remaining'):
                # ignore any entry containing '?' altogether
                if '?' in word:
                    pass
                # if the word contains '-', increase rather than decrease
                elif word.startswith('-'):
                    self.controller.wh_remaining += 1
                    self.update_wordhogger_counter()
                # all other new words consume one from the counter
                else:
                    self.controller.wh_remaining = max(0, self.controller.wh_remaining - 1)
                    self.update_wordhogger_counter()
            self.words_display.insert(0, word)
            self.words_display.itemconfig(0, fg='black')
            self.entry_var.set("")

    def confirm_new(self):
        if messagebox.askyesno("Confirm", "Start a new game? This will lose current progress."):
            self.controller.start_game()

    def confirm_finish(self):
        if messagebox.askyesno("Confirm", "Finish early?"):
            self.controller.end_game()

    def _on_entry(self, *args):
        # strip any spaces and force uppercase
        txt = self.entry_var.get().replace(' ', '').upper()
        self.entry_var.set(txt)
        
    def toggle_pause(self, event=None):
        if not self.paused:
            # pause
            self.paused = True
            if self.timer_id:
                self.after_cancel(self.timer_id)
            self.saved_time = self.controller.time_remaining
            self.draw_blank_board()
            self.word_entry.config(state='disabled')
            self.rorate_allowed = False
        else:
            # resume
            self.paused = False
            self.controller.time_remaining = self.saved_time
            self.draw_board()
            self.word_entry.config(state='normal')
            self.update_timer()    
            self.rotate_allowed = True
        
        
        
class EndScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Container centered frame
        inner = tk.Frame(self)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        # Title and rank
        header = tk.Frame(self)
        header.pack(pady=5)
        # store this Label so we can change it to “Round X/12” in World Tour
        self.header_label = tk.Label(header, text="Game Over", font=("Helvetica",24,"bold"))
        self.header_label.pack()
        self.rank_canvas = tk.Canvas(header, width=100, height=60, highlightthickness=0)
        self.rank_canvas.pack(pady=5)                   
        # Round Score (below rank, above badges)
        self.score_label = tk.Label(header, text="Round Score: 0", font=("Helvetica",18,"bold"))
        self.score_label.pack(pady=(2,5))
        # Badges under title, moved into header beside rank
        self.badge_frame = tk.Frame(header)
        # Position badges with place() for relative centering in header
        self.badge_frame.place(relx=0.8, rely=0.5, anchor='center')
        # Board classification
        self.class_canvas = tk.Canvas(self, height=30, highlightthickness=0)
        self.class_canvas.pack(pady=(5,15))
        # Word list
        fr = tk.Frame(self)
        fr.pack(fill="both", expand=True, pady=5)
        # shrink height so we make room above
        self.listbox = tk.Listbox(fr, font=("Helvetica",14), height=8)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.config(justify='center')
        sb = tk.Scrollbar(fr, command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)
        # Bind double-click after listbox is created
        self.listbox.bind('<Double-Button-1>', self.show_def)

        # Buttons frame
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        # Play Again / Next Round
        self.play_again_btn = tk.Button(
            btn_frame, text="Play Again", font=("Helvetica",16),
            command=controller.start_game
        )
        self.play_again_btn.pack(side="left", padx=5)

        # Word Judge – shows only judged “?WORD” entries
        self.word_judge_btn = tk.Button(
            btn_frame, text="Word Judge", font=("Helvetica",16),
            command=lambda: self._show_judged_popup(self.controller.judged_words),
            state='disabled'
        )
        self.word_judge_btn.pack(side="left", padx=5)

        # Missed Words – shows only the incorrect entries
        self.missed_words_btn = tk.Button(
            btn_frame, text="Missed Words", font=("Helvetica",16),
            command=lambda: self._show_judged_popup(self.controller.incorrect_words),
            state='disabled'
        )
        self.missed_words_btn.pack(side="left", padx=5)

        # Main Menu
        self.main_menu_btn = tk.Button(
            btn_frame, text="Main Menu", font=("Helvetica",16),
            command=lambda: controller.show_frame("MainMenu")
        )
        self.main_menu_btn.pack(side="left", padx=5)
        self.defs = {}

    def draw_rank(self, rank, color):
        self.rank_canvas.delete("all")
        w = self.rank_canvas.winfo_width() or 80
        x, y = w/2, 25
        # outline in 48pt, main in 46pt for extra prominence
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2),(-1,0),(1,0),(0,-1),(0,1)]:
            self.rank_canvas.create_text(x+dx, y+dy, text=rank, font=("Helvetica",48,"bold"), fill='black')
        self.rank_canvas.create_text(x, y, text=rank, font=("Helvetica",46,"bold"), fill=color)

    def display_results(self, uv, us, all_w, all_s, dict_, ps, incorrect, mode):
        # Badges: only show frame if we actually earned any
        # clear out old badges
        for w in self.badge_frame.winfo_children():
            w.destroy()
        badge_map = {
            'Homerun':'homerun',
            'Eagle Eye':'eagleeye',
            'Word Hogger':'wordhogger',
            'Erudite':'erudite',
            'Pottymouth':'pottymouth',
            'Heavyweight': 'heavyweight'
        }
        bonuses = getattr(self.controller, 'last_bonuses', [])
        if bonuses:
            # re-enable our badge area
            self.badge_frame.pack_configure(pady=5)
            for bonus in bonuses:
                for key, badge in badge_map.items():
                    if bonus.startswith(key):
                        img = self.controller.badge_images.get(badge)
                        if img:
                            lbl = tk.Label(
                                self.badge_frame,
                                image=img,
                                bd=0,
                                highlightthickness=0
                            )
                            lbl.pack(side='left', padx=2)
                        break
        else:
            # collapse the badge frame entirely
            self.badge_frame.pack_forget()
        # disable button
        self.play_again_btn.config(state='disabled')
        self.after(3000, lambda: self.play_again_btn.config(state='normal'))
        # update score and classification
        self.score_label.config(text=f"Round Score: {self.controller.total_score}")
        msg, col, val = self.controller.classification_for(ps)
        self.controller.board_potential = val
        self.class_canvas.delete("all")
        w = self.class_canvas.winfo_width() or 400
        x, y = w/2, 12
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            self.class_canvas.create_text(x+dx, y+dy, text=msg, font=("Helvetica",21,"bold"), fill="black")
        self.class_canvas.create_text(x, y, text=msg, font=("Helvetica",21,"bold"), fill=col)
        # Word Hogger bonus message
        num = len(uv)
        thresh = get_wordhogger_threshold(self.controller.board_potential)
        # prepare message frame
        try:
            self.bonus_msg_frame.destroy()
        except:
            pass
        self.bonus_msg_frame = tk.Frame(self)
        if thresh > 0 and num >= thresh:
            # earned Word Hogger bonus
            f1 = tk.Label(self.bonus_msg_frame, text=f"{num}", font=("Helvetica",14,"italic"), fg="green")
            f1.pack(side="left")
            l2 = tk.Label(self.bonus_msg_frame, text=" words found. Well done!", font=("Helvetica",14,"italic"))
            l2.pack(side="left")
        else:
            needed = max(0, thresh - num)
            f1 = tk.Label(self.bonus_msg_frame, text=f"{num}", font=("Helvetica",14,"italic"), fg="black")
            f1.pack(side="left")
            l2 = tk.Label(self.bonus_msg_frame, text=" words found. Find ", font=("Helvetica",14,"italic"))
            l2.pack(side="left")
            f2 = tk.Label(self.bonus_msg_frame, text=f"{needed}", font=("Helvetica",14,"italic"), fg="green")
            f2.pack(side="left")
            l3 = tk.Label(self.bonus_msg_frame, text=" more words next time for a bonus!", font=("Helvetica",14,"italic"))
            l3.pack(side="left")
        self.bonus_msg_frame.pack(pady=(0,10))
        self.listbox.delete(0, tk.END)
        for w in sorted(all_w, key=lambda x: all_s[x], reverse=True):
            txt = f"{w}: {all_s[w]}"
            idx = self.listbox.size()
            self.listbox.insert(tk.END, txt)
            self.defs[txt] = dict_.get(w,"")
            fg = 'green' if w in uv else 'black'
            self.listbox.itemconfig(idx, fg=fg)
            
        # Update the enabled state of our new popup buttons
        self.word_judge_btn.config(
            state='normal' if self.controller.judged_words else 'disabled'
        )
        self.missed_words_btn.config(
            state='normal' if self.controller.incorrect_words else 'disabled'
        )    
            
            
            
    def display(self, total_score, avg_rs, final_rank, badge_totals, best_word, best_score, summary_file):
        # clear previous
        self.info_text.delete("1.0", tk.END)
        # write summary into the text widget
        self.info_text.insert(tk.END, f"Total Score: {total_score}\n")
        self.info_text.insert(tk.END, f"Average RS: {avg_rs:.2f}\n")
        self.info_text.insert(tk.END, f"Final Rank: {final_rank}\n\n")
        self.info_text.insert(tk.END, "Badges Earned:\n")
        for k, v in badge_totals.items():
            self.info_text.insert(tk.END, f" - {k}: x{v}\n")
        self.info_text.insert(tk.END, f"\nTop Word: {best_word} ({best_score} pts)\n\n")
        self.info_text.insert(tk.END, f"Full details saved to:\n{summary_file}")

    def show_def(self, event): #This is the Main Wordlist definition handler
        sel = self.listbox.curselection()
        if not sel:
            return
        txt = self.listbox.get(sel[0])
        # strip off any “: score” suffix
        word_only = txt.split(':',1)[0]
        orig_def = self.defs.get(txt, "")
        # build list of cascading definitions
        defs = []
        current = orig_def
        while True:
            defs.append(current)
            if "=" not in current:
                break
            m = re.search(r"([A-Za-z0-9]+)=", current)
            if not m:
                break
            alias = m.group(1).upper()
            next_def = self.controller.dictionary.get(alias, None)
            if not next_def or next_def == current:
                break
            current = next_def
        # prepare message lines
        msg_lines = []
        for i, d in enumerate(defs, start=1):
            if i == 1:
                msg_lines.append(f"Definition: {d}")
            else:
                msg_lines.append(f"\n\nDefinition {i}: {d}")
        # create popup window
        popup = tk.Toplevel(self)
        popup.title(f"Definition: {word_only}")
        popup.transient(self.controller)
        # build label with smaller default font
        label = tk.Label(popup, text="".join(msg_lines), justify="left")
        label.pack(padx=10, pady=10)
        # Buttons frame
        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=(0,10))
        # WTF? button
        def on_wtf():
            query = f"{txt} {defs[-1]}"
            # strip out any digits or symbols from the last definition
            cleaned_def = re.sub(r'[^A-Za-z\s]', '', defs[-1])
            query = f"{txt} {cleaned_def}"
            img_data = search_image(query)
            if not img_data:
                messagebox.showwarning("WTF?", "No image found.")
                return            
            popup_img = tk.Toplevel(self)
            # show only the raw word in the header
            word = txt.split(':',1)[0]
            popup_img.title(f"Here is what Google Images says {word} looks like:")            
            popup_img.transient(self.controller)
            photo = ImageTk.PhotoImage(data=img_data)
            lbl = tk.Label(popup_img, image=photo, bd=0, highlightthickness=0)
            lbl.image = photo
            lbl.pack(padx=10, pady=10)
            # center this image popup
            popup_img.update_idletasks()
            px = self.controller.winfo_rootx()
            py = self.controller.winfo_rooty()
            pw = self.controller.winfo_width()
            ph = self.controller.winfo_height()
            iw = popup_img.winfo_width()
            ih = popup_img.winfo_height()
            popup_img.geometry(f"{iw}x{ih}+{px + (pw - iw)//2}+{py + (ph - ih)//2}")
        wtf_btn = tk.Button(btn_frame, text="WTF?", command=on_wtf)
        wtf_btn.pack(side='left', padx=5)
        ok_btn = tk.Button(btn_frame, text="OK", command=popup.destroy)
        ok_btn.pack(side='left', padx=5)
        # center popup over main window
        popup.update_idletasks()
        px = self.controller.winfo_rootx()
        py = self.controller.winfo_rooty()
        pw = self.controller.winfo_width()
        ph = self.controller.winfo_height()
        ww = popup.winfo_width()
        wh = popup.winfo_height()
        popup.geometry(f"{ww}x{wh}+{px + (pw - ww)//2}+{py + (ph - wh)//2}")
        # focus OK button and bind Enter
        ok_btn.focus_set()
        popup.bind('<Return>', lambda e: ok_btn.invoke())

    def _show_judged_popup(self, words):
        """Show a small centered popup listing last round’s ?WORDs (no '?'), with defs."""
        popup = tk.Toplevel(self)
        popup.title("Queried Words")
        popup.transient(self.controller)

        # strip both leading and trailing '?' and build defs map
        clean = [w.strip('?') for w in words]
        defs_map = {w: self.controller.dictionary.get(w, "") for w in clean}

        # Listbox styled like the main one: same font, bigger size,
        # and color entries green/red by validity
        lb = tk.Listbox(
            popup,
            font=("Helvetica", 14),
            height=min(len(clean) + 2, 10),
            width=30
        )
        for idx, w in enumerate(clean):
            lb.insert(tk.END, w)
            fg = 'green' if w in self.controller.dictionary else 'red'
            lb.itemconfig(idx, fg=fg)
        lb.pack(padx=10, pady=10)

        # double-click handler for showing definitions
        def on_def(event):
            sel = lb.curselection()
            if not sel:
                return
            word = lb.get(sel[0])
            # build cascading definition chain
            d = defs_map.get(word, "")
            chain = []
            cur = d
            while True:
                chain.append(cur)
                if '=' not in cur:
                    break
                m = re.search(r"([A-Za-z0-9]+)=", cur)
                if not m:
                    break
                alias = m.group(1).upper()
                nxt = self.controller.dictionary.get(alias)
                if not nxt or nxt == cur:
                    break
                cur = nxt

            # format as numbered definitions
            numbered = [f"Definition {i}: {defn}" for i, defn in enumerate(chain, start=1)]
            text = "\n\n".join(numbered)

            # create definition popup
            msg = tk.Toplevel(popup)
            msg.title(f"Definition: {word}")
            msg.transient(popup)
            tk.Label(msg, text=text, justify="left").pack(padx=10, pady=10)

            # add WTF? and OK buttons in definition popup
            btn_frame = tk.Frame(msg)
            btn_frame.pack(pady=(0, 10))
            def on_wtf_def():
                # lookup image for final definition
                final = chain[-1]
                import utils
                img_data = utils.search_image(f"{word} {final}")
                if not img_data:
                    messagebox.showwarning("WTF?", "No image found.")
                    return
                popup_img = tk.Toplevel(msg)
                popup_img.title(f"Google Images: {word}")
                popup_img.transient(msg)
                photo = ImageTk.PhotoImage(data=img_data)
                tk.Label(popup_img, image=photo).pack(padx=10, pady=10)
                popup_img.image = photo

            ok_btn = tk.Button(btn_frame, text="OK", command=msg.destroy)
            ok_btn.pack(side='right', padx=5)
            wtf_btn = tk.Button(btn_frame, text="WTF?", command=on_wtf_def)
            wtf_btn.pack(side='right', padx=5)

            # center the definition popup
            msg.update_idletasks()
            mw, mh = msg.winfo_width(), msg.winfo_height()
            sw, sh = msg.winfo_screenwidth(), msg.winfo_screenheight()
            mx, my = (sw - mw) // 2, (sh - mh) // 2
            msg.geometry(f"{mw}x{mh}+{mx}+{my}")

            ok_btn.focus_set()
            msg.bind('<Return>', lambda e: ok_btn.invoke())

                # bind double-click to our handler; swallow errors if widget no longer exists
        try:
            lb.bind('<Double-Button-1>', on_def)
        except tk.TclError:
            pass

        # center the main popup over the main window
        popup.update_idletasks()
        pw, ph = popup.winfo_width(), popup.winfo_height()
        px = self.controller.winfo_rootx()
        py = self.controller.winfo_rooty()
        cw, ch = self.controller.winfo_width(), self.controller.winfo_height()
        popup.geometry(f"{pw}x{ph}+{px + (cw - pw)//2}+{py + (ch - ph)//2}")
        popup.lift()
        popup.grab_set()
        popup.wait_window()




            
class SummaryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid(sticky="nsew")

        # Header
        header = tk.Frame(self)
        header.pack(pady=10)
        self.title_label = tk.Label(
            header, text="World Tour Results:", font=("Helvetica", 24, "bold")
        )
        self.title_label.pack()

        # Total Score
        self.score_label = tk.Label(self, text="", font=("Helvetica", 18))
        self.score_label.pack(pady=(5,10))

        # Large rank letter
        self.rank_canvas = tk.Canvas(self, width=120, height=80, highlightthickness=0)
        self.rank_canvas.pack(pady=5)

        # Badges (vertical list)
        self.badges_frame = tk.Frame(self)
        self.badges_frame.pack(pady=10)

        # Top word display
        self.topword_frame = tk.Frame(self)
        self.topword_frame.pack(pady=10)
        self.topword_prefix = tk.Label(
            self.topword_frame, text="Top Word:", font=("Helvetica", 18, "bold")
        )
        self.topword_prefix.pack(side="left")
        self.topword_value = tk.Label(
            self.topword_frame, text="", font=("Helvetica", 18, "bold"), fg="green"
        )
        self.topword_value.pack(side="left", padx=(5,0))

        # Save & Exit button
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(
            btn_frame,
            text="Save & Exit",
            font=("Helvetica", 14),
            command=lambda: controller.show_frame("MainMenu")
        ).pack()

    def display(
        self,
        total_score: int,
        avg_rs: float,
        final_rank: str,
        badge_totals: dict[str,int],
        best_word: str,
        best_score: int,
        summary_file: str
    ):
        # 1) Total score
        self.score_label.config(text=f"Total Score: {total_score}")

        # 2) Final rank, large & colored
        _, color, _ = get_rank_info(avg_rs)
        self.rank_canvas.delete("all")
        w = self.rank_canvas.winfo_width() or 120
        x, y = w/2, 40
        # black outline
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            self.rank_canvas.create_text(
                x+dx, y+dy,
                text=final_rank,
                font=("Helvetica", 48, "bold"),
                fill="black"
            )
        # colored main letter
        self.rank_canvas.create_text(
            x, y,
            text=final_rank,
            font=("Helvetica", 46, "bold"),
            fill=color
        )

        # 3) Badges: only those earned >0, vertical
        for child in self.badges_frame.winfo_children():
            child.destroy()
        badge_map = {
            'Homerun': 'homerun',
            'Eagle Eye': 'eagleeye',
            'Word Hogger': 'wordhogger',
            'Erudite': 'erudite',
            'Pottymouth': 'pottymouth',
            'Heavyweight': 'heavyweight'
        }
        for name, count in badge_totals.items():
            if count > 0 and name in badge_map:
                # frame with no border/highlight
                row = tk.Frame(
                    self.badges_frame,
                    bd=0,
                    highlightthickness=0,
                    relief='flat'
                )
                row.pack(anchor="w", pady=2)
                img = self.controller.badge_images.get(badge_map[name])
                if img:
                    # image label without any outline
                    lbl = tk.Label(
                        row,
                        image=img,
                        bd=0,
                        highlightthickness=0,
                        relief='flat'
                    )
                    lbl.image = img
                    lbl.pack(side="left")
                # count label with no outline
                tk.Label(
                    row,
                    text=f"x{count}",
                    font=("Helvetica", 16),
                    bd=0,
                    highlightthickness=0,
                    relief='flat',
                    bg=row['bg']      # match background to parent
                ).pack(side="left", padx=(5,0))

        # 4) Top word with its score in green
        self.topword_value.config(text=f"{best_word} ({best_score} pts)")