import random

class Bot:
    def __init__(self, window_size=5):
        self.history = []
        self.window_size = window_size
        self.possible_moves = ['R', 'P', 'S']
        self.counter_moves = {'R': 'P', 'P': 'S', 'S': 'R'}

        # For adaptive strategy
        self.predictors = {
            'random': self.random_predict,
            'freq': self.freq_predict,
            'markov': self.markov_predict,
        }

        # Store recent performance: (1) win, (0) draw, (-1) lose
        self.performance = {name: [] for name in self.predictors}
        self.last_move = None
        self.last_strategy = None

    def random_predict(self):
        """Simply picks one move randomly"""
        return random.choice(self.possible_moves)

    def freq_predict(self):
        """Picks the most frequent move"""
        if not self.history:
            return self.random_predict()
        counts = {move: self.history.count(move) for move in self.possible_moves}
        return max(counts, key=counts.get)

    def markov_predict(self):
        """Picks a move based on Markov strategy"""
        if not self.history or len(self.history) < self.window_size:
            return self.random_predict()

        window = tuple(self.history[-self.window_size:])
        future_moves = {} # Store moves tend to come next after that pattern

        for i in range(len(self.history) - self.window_size):
            past_sequence = tuple(self.history[i:i+self.window_size])
            if past_sequence == window and i + self.window_size < len(self.history):
                next_move = self.history[i + self.window_size]
                future_moves[next_move] = future_moves.get(next_move, 0) + 1

        # Pick the most likely move after the pattern
        if future_moves:
            best_prediction = max(future_moves, key=future_moves.get)
            return best_prediction
        else:
            # If full window didn't match anything, try smaller window
            for size in range(1, self.window_size):
                smaller_window = tuple(self.history[-size:])
                smaller_future_moves = {}
                for i in range(len(self.history) - size):
                    past_smaller_sequence = tuple(self.history[i:i+size])
                    if past_smaller_sequence == smaller_window and i + size < len(self.history):
                        next_move = self.history[i + size]
                        smaller_future_moves[next_move] = smaller_future_moves.get(next_move, 0) + 1
                
                if smaller_future_moves:
                    return max(smaller_future_moves, key=smaller_future_moves.get)
            
            # If none of the windows ever matched anything in the history
            return self.random_predict()

    def play(self):
        """Play a counter move based on prediction"""
        scores = {}
        for name, results in self.performance.items():
            if results:
                wins = results.count(1)
                draws = results.count(0)
                total = len(results)
                score = (wins + 0.2 * draws) / total # Weighted score
                scores[name] = score
            else:
                scores[name] = 0.5 # Neutral score

        # Best strategy is the one with the highest score!
        best_strategy = max(scores, key=scores.get)
        predicted_move = self.predictors[best_strategy]()

        self.last_strategy = best_strategy
        self.last_move = self.counter_moves[predicted_move]
        return self.last_move

    def update(self, opponent_move):
        """Update the bot history and performance"""
        self.history.append(opponent_move)

        if self.last_move and self.last_strategy:
            result = self.get_result(self.last_move, opponent_move)
            self.performance[self.last_strategy].append(result)

            # Trim the performance into 30 lastest results
            if len(self.performance[self.last_strategy]) > 30:
                self.performance[self.last_strategy] = self.performance[self.last_strategy][-30:]

    def get_result(self, bot_move, opponent_move):
        """Helper function that calculates the result based on given moves"""
        if bot_move == opponent_move:
            return 0
        elif self.counter_moves[bot_move] == opponent_move:
            return -1
        else: return 1

bot = Bot()

def player(prev_play, opponent_history=[]):
    global bot

    if prev_play:
        bot.update(prev_play)

    return bot.play()