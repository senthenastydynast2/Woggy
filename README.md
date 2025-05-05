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
6. [Definitions and "WTF?" Search](#definitions) ❓
7. [Coming Soon](#coming-soon) 😏

##  Installation

1. If you don't already have Python installed, install it by [visiting here](https://www.python.org/downloads/). 
2. Download the [game .zip file](https://github.com/senthenastydynast2/Woggy/archive/refs/heads/main.zip).  
3. Unpack it to a folder of your choice.  
4. Run `run.bat`.

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

The board's classification nickname is displayed in the End Screen, and it ranges from `Impossible Board!` all the way to `Godlike Board!` depending on its potential. There are currently 32 total categories where a board can fit into, each with its own unique timer and scoring parameters.

<div align="center">
<img src="https://github.com/user-attachments/assets/297442e1-6920-482c-bad1-2d836d779447" />
</div>  

<h4 align="center">*An example of a board with very high score potential, showing a purplish background to indicate its potential. </h4>

### Score Logging

At the end of each round (or a World Tour game), a text file will be automatically be generated under the **Scores** folder with the date on the title and a breakdown of the entire round. Useful for keeping track of high scores!

### Options

-**Tile Size**: This will resize the board tiles for better readability. Please be advised, since the game is still extremely early in development, I haven't yet tested all tile sizes to look good.

-**Word Judge**: Turning this off will turn off the comments you get at the end of each round. For those who prefer a judgement-free Woggy experience!

All options and latest preferences are automatically saved in `Settings\settings.json`.


## Scoring Rules

Each tile in Woggy scores the same amount as it does in an official Scrabble board * 10. For example, E = 10, F = 40, Q = 100, etc. In its pure form, the word `SQUADS` would be worth 160 points.

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

With this scoring logic, `SQUADS` will be worth 280 points, instead of its base 160. While this scoring system might seem a bit overboard, keep in mind that words longer than 9 or 10 are quite rare to find. In the rare occassion that one does exist, one will be properly compensated for finding it.

### Rank Determination

Depending on your performance, you will be shown a rank letter in your end screen. These range from `F-` all the way to a legendary `SS`.

This score is calculated by several factors, but at its core, it is based on what percentage of the potential score you earned in a given board. For example, only getting a 5% score will net you an `F-`, but netting 45% will get you a solid `A`. There are a few more factors to consider, though. "Extreme" boards (very closed or very open) have a handicap to offset scores in an effort to make them more balanced. This means that in order to get a high rank in a board that only contains 12 words, you will need to find more than 45% of them to get an A or higher because of the handicap.

If this seems unfair, you'll be pleased to know that the opposite is true for longer boards. Very open boards naturally contain loads of esoteric and rare words that players are not expected to guess. Therefore, a handicap in your favor is applied to your score at the end of the round. The specific handicaps will be visible in your **Scores** folder breakdown.

## Game Modes

- **Standard:** No penalty whatsoever for guessing incorrect words. *Recommended for casual players*.

- **Hardcore:** If a word you entered is not in the dictionary, at the end of the round, you will be penalized for half of that word's score, including the bonus. So if `SQUADS` was an invalid word, you would be penalized 140 points. <br> *Recommended for competitive players who want to put their vocabulary to the test!*

**IMPORTANT**: Words that cannot be connected in the board (ie. words that aren't actually formable) do not count as incorrect words, they are simply ignored (except for badge counters, see [Badges](#badges)). The same applies to 1-and-2 letter words and duplicate entries.

### Special Commands (for Hardcore mode only!):

- **-WORD**: Word deletion. Typing `-WORD` will delete an entry from the list. Since Hardcore penalizes for incorrect words, if you made a typo, delete it by typing `-YOURTYPOWORD` in the input box.
  
- **?WORD** or **WORD?**: Word query. Let's say you come across a word you aren't sure is valid. You don't want to risk getting it wrong, but the curiosity is killing you and you want to know if it's a valid word. Simply type `?YOURWORD` or `YOURWORD?`, and at the end of the round, you will be able to check if the word was valid or not, without it affecting your score or badges whatsoever.

<div align="center">
<img src="https://github.com/user-attachments/assets/33ffb855-1c8a-4cd4-85bd-4421f9d9af67" />
</div>  

<h5 align="center">*In Hardcore mode, if you guessed any words incorrectly or you looked up any words, the buttons above will allow you to see those words. </h5>

### Game Sub-Types

- **Quick Play:** A completely random board is generated. Simple!

- **World Tour:** Do you have what it takes to slay across all different board types? Go through 10 different boards which range from very closed fast boards to very open long boards! The boards are all still randomly generated, however, you will only play one board of each classification. For example, you will play one extremely short board, one kinda short board, one slightly short board, one average board `...` one extremely open board. The order of these boards is randomized, so pay attention to the background colors so you can react quickly to the fast boards! <br><br> At the end of each round, you will be given a rating and score exactly the same way as in Quick Play, one for each round. At the end of the 10th round, you will see a special end screen with your total score, badges earned and your **average** rating across all boards! Perhaps some folks are good at short fast words, and others are better at long words and slower play. This game mode balances that since it will test you at 10 different board types!

<div align="center">
<img src="https://github.com/user-attachments/assets/b6cb9e4e-edfa-4d41-bffa-5c90bc666da5" />
</div>

<h5 align="center">*The World Tour summary screen.</h5>

**IMPORTANT**: Board generation for World Tour can be very CPU-intensive, which means hang time might happen during board generation which might be mistaken for a game crash. I plan to optimize the algorithm responsible, but for now, just be patient!

- **Word Monster**: *Coming Soon!*

- **Spanglish Bonanza**: *Coming Soon!*

## Badges

Badges are your secret weapon in achieving higher ranks in your games. When specific criteria is met, your badge is awarded with a popup message at the end of the round letting you know how many (if any) badges you earned, and a specific percentage bonus is applied to your final score (the bonuses stack!):

<div align="center">
  
  ### 🏅 Badge List
  
<table>
  <thead>
    <tr>
      <th>Icon</th>
      <th>Badge</th>
      <th>Requirement</th>
      <th>Bonus</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><img src="https://github.com/user-attachments/assets/51d567bd-46e5-4225-85b6-d7a39cde2a88" width="60"/></td>
      <td><strong>Homerun</strong></td>
      <td>Awarded for guessing a word whose score is equal to the highest scoring word possible.</td>
      <td>5%</td>
    </tr>
    <tr>
      <td><img src="https://github.com/user-attachments/assets/b5a2f200-d6fd-4c94-9e6a-18fa068c16d6" width="60"/></td>
      <td><strong>Eagle Eye</strong></td>
      <td>Awarded for guessing a word whose length is equal to the longest word possible.<br>It is often earned in tandem with Homerun, but not always.</td>
      <td>5%</td>
    </tr>
    <tr>
      <td><img src="https://github.com/user-attachments/assets/d69754bc-057a-428d-b654-9c71a5e7f940" width="60"/></td>
      <td><strong>Word Hogger</strong></td>
      <td>Awarded for hogging all them words! Any valid words counts towards this badge.<br>The number of words required is shown in the top right corner, next to the gray pig.*</td>
      <td>5%</td>
    </tr>
    <tr>
      <td><img src="https://github.com/user-attachments/assets/a999b998-493b-458c-84da-00d49841f182" width="60"/></td>
      <td><strong>Erudite</strong></td>
      <td><strong><em>Hardcore Mode only!</em></strong><br>You thought playing in Hardcore wasn't worth it? With this badge, you get a reward for your risk!<br>Awarded when the player gets zero incorrect words.</td>
      <td>15%</td>
    </tr>
    <tr>
      <td><img src="https://github.com/user-attachments/assets/6f1a110b-8f0e-4ef5-830a-26d24fb1a435" width="60"/></td>
      <td><strong>Heavyweight</strong></td>
      <td>Awarded for guessing 5 or more words whose length is equal or higher than 7.<br>A counter in the top left is displayed to help the player keep count of these.*</td>
      <td>5%</td>
    </tr>
    <tr>
      <td><img src="https://github.com/user-attachments/assets/52fe0f92-a90c-4832-9b5c-38ab7726ce5f" width="60"/></td>
      <td><strong>Pottymouth</strong></td>
      <td>A badge that is more luck-based than any other!<br>Awarded for getting 3 or more words whose definition is: "an offensive word".**</td>
      <td>5%</td>
    </tr>
    <tr>
      <td><img src="https://github.com/user-attachments/assets/0382c05a-dc30-4530-ae8d-047a505ff0eb" width="60"/></td>
      <td><strong>Word Monster</strong></td>
      <td><strong><em>Coming soon!</em></strong></td>
      <td>???</td>
    </tr>
  </tbody>
</table>
<br>
*Please note: The counters for both Word Hogger and Heavyweight don't check if an entered word can be formed nor if the word is valid/invalid. Therefore the counter will show a tick even when one isn't actually earned. This is intended, but may be adjusted in the future for Standard mode.
<br>
<br>
**In the English dictionary provided, there are currently 227 words that fit this criteria. Happy swearing!
</div>

## Definitions

### Dictionary Source

Before getting into definitions, you may wonder: What makes a valid word valid? Who decides? Why is my favorite WWF word shown as invalid? For which I would have you -- the smart lexicon inquisitor -- take a look at `Dictionaries\About_English.txt` where I go in an in-depth explanation as to where this dictionary comes from, and why it is the one chosen for this game (as well as for my upcoming Scrabble game!).

### Definition Lookup

To look up a definition, simply double-click it. When doing so, you may see something like this:

<div align="center">
<img src="https://github.com/user-attachments/assets/c30c5e90-b780-4d51-af3a-c98708fa2ff8" />
</div>

<br>
Here's how to interpret the definition:

- **Definition 1**: When you see any word that is preceded by a `=`, it is referring to an alternate spelling or word to refer to the queried word. <br> In this case, it is telling us that `KRAY` is the same as `KRAI`. But that's not a satisfying answer, is it?

- **Definition 2**: The word `KRAI` is automatically searched for your convenience, and we get to the root meaning. An administrative territory in Russia. If any more references are nested, those will be looked up next.

The `n` means the word is a noun. In brackets, you will find how the word is conjugated or pluralized. In this case, it is simply pluralized by adding an S. `KRAYS` and `KRAIS`.

These definitions can iterate a lot in some cases, but hopefully, it is clear enough to get an idea of what the word actually means.

### WTF? Button

Aaah, the classic scenario: You look up a word, you read the definition, and all you can think of is... WTF?

Well, wonder no more! When you press the `WTF?` button, a Google Images search API will automatically fetch an image of the Word + definition, in an attempt to illustrate what the mysterious word actually is. Like this:


<div align="center">
<img src="https://github.com/user-attachments/assets/95ab5e7e-4c5d-43ba-8a5a-883d8a01d2c1" />
</div>


This completely optional and convenient service is provided using a free API from a website called [Scraping Dog](https://www.scrapingdog.com/). Please keep in mind that API services usually have a limited number of uses before you have to pay. For the sake of providing you a completely functional game in this early phase, I have included my own API key built-in since I speculate not a whole bunch of people are going to swarm this game on release.

In the future, though, that API key may cease to function and you will be expected to provide your own. Again, the game works completely fine without this function, you don't need to use it. But if you can, show your support for the people who make these APIs by checking out their website and signing up for your own key (they offer free keys as well). Once you do get your own API key, you can replace the one found in `utils.py`, simply open the file with any text editor and replace the API key in line 18.


## Coming Soon 

- **Online Multiplayer**

- **Sound Effects**

- **More Tile Skins**, especially if you don't dig the My Little Pony ones I made! 😁

- **iOS / Android Port**

- **Spanish Dictionary**

- **Final Boss Round for World Tour mode (secret!)**

- **Bigger boards, new game modes, and more!**

- **A place where you can buy me a coffee if you enjoy the game to keep supporting its and future projects' development!**
