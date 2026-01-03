Connect 4 – Alpha-Beta Pruning AI

--> OVERVIEW

This project implements a Connect 4 game with a graphical interface and an Artificial Intelligence player based on the Minimax algorithm with Alpha–Beta pruning.

The AI is designed to play competitively by combining:

  game tree search (Alpha–Beta),

  heuristic board evaluation,

  tactical rules (immediate win detection, blocking, fork creation and prevention),

  move safety checks to avoid suicidal plays.

The application allows human vs AI, AI vs AI, and human vs human matches with adjustable AI depth.


--> FEATURES

Graphical interface built with Tkinter

Fully playable Connect 4 game

AI using Minimax + Alpha–Beta pruning

Configurable AI depth (difficulty level)

Tactical awareness:

  Immediate win detection

  Blocking opponent wins

  Fork creation and fork prevention

  Avoidance of moves giving instant victory to the opponent

Heuristic-based evaluation for non-terminal states

Optimized move ordering for better pruning efficiency


--> AI Strategy Summary

The AI move selection follows a priority-based decision pipeline:

Play an immediate winning move if available

Block opponent’s immediate winning move

Prevent opponent forks (multiple simultaneous threats)

Create a fork if possible

Filter out suicidal moves (moves that give opponent a win)

Use Alpha–Beta Minimax to evaluate remaining moves

Select the move with the highest evaluation score

This hybrid approach ensures strong tactical play even with limited search depth.


--> Heuristic Evaluation Function

Each board state is evaluated by scanning all possible windows of four cells:

  Horizontal

  Vertical

  Diagonal (both directions)

Scoring considers:

  Winning positions

  Immediate and future threats

  Opponent threats

  Center column control

  Two-in-a-row and three-in-a-row patterns

  Fork opportunities (highly weighted)

The heuristic was refined iteratively through extensive testing and debugging.


--> Installation & Requirements
-Requirements

  Python 3.9+

  numpy

Tkinter is included by default with most Python distributions.

-Installation

Clone the repository:

  git clone https://gitlab.com/ali-essarsare/ai-project.git
  cd connect4-alpha-beta


-Install dependencies:

  pip install numpy


--> Running the Game

Start the game with:

  python connect4.py


The graphical window will open automatically.


--> How to Play

Select player types for Player 1 and Player 2

  human

  AI: alpha-beta level X

Click New Game

If playing as a human, click a column to drop a disk

The game ends with a win or a draw


--> Project Structure
.
├── connect4.py        # Main application and AI logic
├── README.md          # Project documentation


--> Known Limitations

High AI levels may result in longer thinking times

Strong defensive play often leads to draws, which is expected for optimal Connect 4 strategies

The AI does not use transposition tables or opening books


--> Lessons Learned

Pure Minimax is insufficient without tactical heuristics

Fork detection is critical for strong Connect 4 play

Evaluation weight tuning significantly affects AI behavior

Alpha–Beta pruning efficiency depends heavily on move ordering

Iterative testing is essential for building reliable game AI


--> Possible Improvements

Add transposition tables (hashing)

Implement iterative deepening

Improve evaluation with pattern databases

Add move statistics and pruning metrics

Optimize performance for higher depths


--> License

This project is intended for educational purposes.
Feel free to modify and experiment with the code.
