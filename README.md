<h1 align="center">Woggy</h1>

<p align="justify">
  Woggy is basically what Boggle always wanted to be, if only it had been born in the Information Age! Dynamic timer, built-in definitions, and an overhaul to the scoring system that rebalances it in favor of long words!
</p>

<div align="center">
  <img src="https://github.com/user-attachments/assets/b64cdead-219d-4547-ab2d-f964d4598844" alt="Gameplay screenshot" />
</div>

---

## 📚 Table of Contents
1. [Installation](#installation) 🛠️
2. [How to Play / Core Mechanics](#how-to-play--core-mechanics) ▶️
3. [Scoring Rules](#scoring-rules) ✏️
4. [Game Modes](#game-modes) ⚾
5. [Badges](#badges) 🎖️
6. [Definitions and "WTF?" Search](#definitions-and-wtf-search) ❓
7. [Coming Soon](#coming-soon) 😏

##  Installation

1. If you don't already have Python installed, install it by [visiting here](https://www.python.org/downloads/). 
2. Download the [game .zip file](https://github.com/senthenastydynast2/Woggy/archive/refs/heads/main.zip).  
3. Unpack it to a folder of your choice.  
4. Run **run.bat**.

##  How to Play / Core Mechanics

If you don't know how to play Boggle, I suggest you look that up first, since the core gameplay is identical to Boggle. Search for words and type away. Only words 3 letters and up are considered, and you can't go over the same letter twice.

### Controls

- **Spacebar**: Rotates the board clockwise. This does not alter the current tile distribution, but is very useful in getting a new perspective on the board.
- **ESC:** Pauses the game. The timer freezes, and tiles go blank until it is unpaused.

### Board Generation

Depending on your game type, a board will be generated at random (no curated boards here, unlike other Boggle wannabe apps!) based on a probability chance for each letter. The probability of a given letter to appear on the board is the same as that of in a game of Scrabble. For example, out of the 100 tiles in a standard Scrabble game, "E" has 12 tiles, and "Q" has 1. Therefore, E has a 12% chance of appearing in a given tile, and Q has a 1% chance. This creates a natural distribution of letters that would be as similar as possible to a competitive Scrabble game.

### Summary Screen

At the end of each round, you will be shown a summary of your performance, including your rank letter, round score, badges earned, a list of possible words that you missed (in black) and words that you correctly guessed (in green) with their respective scores:

<div align="center">
<img src="https://github.com/user-attachments/assets/ffb88c3f-f453-4c9d-98af-696d28d762ac" />
</div>  

### Board Classification (Background Colors)

What makes Woggy unique to other Boggle clones is its dynamic timer and scoring system. Why would we play for 3:00 minutes on a board that only has 10 words? When you start a board, the total possible score for it is calculated, and a board classification is assigned to it depending on how much potential there is on the board. For very closed boards, the timer is shrunk to as little as 15 seconds and the background turns **red** to indicate a sense of urgency. This type of board will more challenge your speed on finding the few words available. On the other hand, boards with huge score potentials have more exotic background colors, such as sky blue, purple, and green, and feature much longer times (up to 300 seconds!). 

The background color gives you a hint on how to play: You will want to hurry up on the reddish boards and change your playstyle for more relaxed play on lighter-colored boards.

The board's classification nickname is displayed in the End Screen, and it ranges from **Impossible Board!** all the way to **Godlike Board!** depending on its potential. There are currently 32 total categories where a board can fit into, each with its own unique timer and scoring parameters.

<div align="center">
<img src="https://github.com/user-attachments/assets/297442e1-6920-482c-bad1-2d836d779447" />
</div>  

<h4 align="center">*An example of a board with very high score potential, showing a purplish background to indicate its potential. </h4>

### Score Logging

At the end of each round (or a World Tour game), a text file will be automatically be generated under the **Scores** folder with the date on the title and a breakdown of the entire round. Useful for keeping track of high scores!

## Scoring Rules

Each tile in Woggy scores the same amount as it does in an official Scrabble board * 10. For example, E = 10, F = 40, Q = 100, etc. In its pure form, the word SQUADS would be worth 160 points.

The main difference in scoring is that longer words now have a much higher weight to them due to **score multipliers**. The longer the word, the higher the score multiplier (as opposed to a measly flat bonus the original Boggle grants). This is a great implementation for those who love to seek long words in the board, and it properly compensates players who have the skill required to find them. Here is how much each word is affected by its length:


<div align="center">

| Word Length | Multiplier |
|-------------|------------|
| 3 letters   | **1x**     |
| 4 letters   | **1.25x**  |
| 5 letters   | **1.5x**   |
| 6 letters   | **1.75x**  |
| 7 letters   | **2x**     |
| 8 letters   | **2.5x**   |
| 9 letters   | **3x**     |
| 10 letters  | **4x**     |
| 11 letters  | **5x**     |
| 12 letters  | **6x**     |
| 13 letters  | **7x**     |
| 14 letters  | **8x**     |
| 15 letters  | **10x**    |
| 16 letters  | **12x**    |

</div>
With this scoring logic, SQUADS will be worth 280 points, instead of its base 160. While this scoring system might seem a bit overboard, keep in mind that words longer than 9 or 10 are quite rare to find. In the rare occassion that one does exist, one will be properly compensated for finding it.

### Rank Determination

Depending on your performance, you will be shown a rank letter in your end screen. These range from "**F-**" all the way to a legendary "**SS**".

This score is calculated by several factors, but at its core, it is based on what percentage of the potential score you earned in a given board. For example, only getting a 5% score will net you an F-, but netting 45% will get you a solid A. There are a few more factors to consider, though. "Extreme" boards (very closed or very open) have a handicap to offset scores in an effort to make them more balanced. This means that in order to get a high rank in a board that only contains 12 words, you will need to find more than 45% of them to get an A or higher because of the handicap.

If this seems unfair, you'll be pleased to know that the opposite is true for longer boards. Very open board naturally contain loads of esoteric and rare words that players are not expected to guess. Therefore, a handicap in your favor is applied to your score at the end of the round. The specific handicaps will be visible in your **Scores** folder breakdown.

## Game Modes

- **Standard:** No penalty whatsoever for guessing incorrect words. *Recommended for casual players*.

- **Hardcore:** If a word you entered is not in the dictionary, at the end of the round, you will be penalized for half of that word's score, including the bonus. So if "SQUADS" was an invalid word, you would be penalized 140 points. <br> *Recommended for competitive players who want to put their vocabulary to the test!*

**IMPORTANT**: Words that cannot be connected in the board (ie. words that aren't actually formable) do not count as incorrect words, they are simply ignored (except for badge counters, see [Badges](#badges)). The same applies to 1-and-2 letter words.

### Special Commands (for Hardcore mode only!):

- **-WORD**: Word deletion. Typing -WORD will delete an entry from the list. Since Hardcore penalizes for incorrect words, if you made a typo, delete it by typing -YOURTYPOWORD in the input box.
  
- **?WORD** or **WORD?**: Word query. Let's say you come across a word you aren't sure is valid. You don't want to risk getting it wrong, but the curiosity is killing you and you want to know if it's a valid word. Simply type ?YOURWORD or YOURWORD?, and at the end of the round, you will be able to check if the word was valid or not, without it affecting your score or badges whatsoever.

<div align="center">
<img src="https://github.com/user-attachments/assets/33ffb855-1c8a-4cd4-85bd-4421f9d9af67" />
</div>  

<h5 align="center">*In Hardcore mode, if you guessed any words incorrectly or you looked up any words, the buttons above will allow you to see those words. </h5>

### Game Sub-Types

- **Quick Play:** A completely random board is generated. Simple!

- **World Tour:** Do you have what it takes to slay across all different board types? Go through 10 different boards which range from very closed fast boards to very open long boards! The boards are all still randomly generated, however, you will only play one board of each classification. For example, you will play one extremely short board, one kinda short board, one slightly short board, one average board (...) one extremely open board. The order of these boards is randomized, so pay attention to the background colors so you can react quickly to the fast boards! <br><br> At the end of each round, you will be given a rating and score exactly the same way as in Quick Play, one for each round. At the end of the 10th round, you will see a special end screen with your total score, badges earned and your **average** rating across all boards! Perhaps some folks are good at short fast words, and others are better at long words and slower play. This game mode balances that since it will test you at 10 different board types!

<div align="center">
<img src="https://github.com/user-attachments/assets/b6cb9e4e-edfa-4d41-bffa-5c90bc666da5" />
</div>

<h5 align="center">*The World Tour summary screen.</h5>

Please note, some boards might share the same nickname, (for example, you might go through 2 different "Average Boards"), but they are actually slightly different from each other. This is not a bug.

**IMPORTANT**: Board generation for World Tour can be very CPU-intensive, which means hang time might happen which might be mistaken for a game crash. I plan to optimize the algorithm responsible, but for now, just be patient!

- **Word Monster**: *Coming Soon!*

- **Spanglish Bonanza**: *Coming Soon!*

