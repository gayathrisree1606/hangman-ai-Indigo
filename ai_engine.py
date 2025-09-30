
import re
from typing import List, Set, Dict
from collections import Counter


class HangmanAI:
    def __init__(self, dictionary_path: str = "words.txt"):
        
        self.full_dictionary = self._load_dictionary(dictionary_path)
        self.current_dictionary = self.full_dictionary.copy()
        self.guessed_letters: Set[str] = set()

        # Common letter frequency in English (fallback strategy)
        self.common_letters = 'etaoinshrdlcumwfgypbvkjxqz'

    def _load_dictionary(self, path: str) -> List[str]:
        
        try:
            with open(path, 'r') as f:
                words = [w.strip().lower() for w in f.readlines()]
                words = [w for w in words if w.isalpha()]
                return words
        except FileNotFoundError:
            print(f"⚠ Warning: {path} not found. Using minimal fallback dictionary.")
            return ['flight', 'airline', 'airport', 'boarding', 'ticket']

    def reset(self):
       
        self.current_dictionary = self.full_dictionary.copy()
        self.guessed_letters.clear()

    def _pattern_to_regex(self, pattern: str) -> str:
        letters = pattern.strip().lower().split()
        regex = ''.join(['.' if l in ['__','*'] else l for l in letters])
        return f'^{regex}$'

    def _filter_dictionary(self, pattern: str, guessed_letters: Set[str]) -> List[str]:
        
        regex_pattern = self._pattern_to_regex(pattern)
        regex = re.compile(regex_pattern)
        letters = pattern.split()
        word_length = len(letters)
        pattern_letters = set([l for l in letters if l != '__'])

        filtered = []
        for word in self.current_dictionary:
            if len(word) != word_length:
                continue
            if not regex.match(word):
                continue
            # Exclude words containing letters guessed but not in the pattern
            wrong_guesses = guessed_letters - pattern_letters
            if any(letter in word for letter in wrong_guesses):
                continue
            filtered.append(word)

        return filtered

    def _calculate_letter_frequencies(self, words: List[str], guessed_letters: Set[str]) -> Dict[str, float]:
        
        if not words:
            return {}

        letter_counts = Counter()
        position_weights: Dict[tuple, int] = {}

        for word in words:
            for pos, letter in enumerate(word):
                if letter not in guessed_letters:
                    letter_counts[letter] += 1
                    key = (letter, pos)
                    position_weights[key] = position_weights.get(key, 0) + 1

        scores = {}
        for letter in letter_counts:
            base_score = letter_counts[letter] / len(words)
            positions = [pos for (let, pos) in position_weights if let == letter]
            diversity_bonus = len(set(positions)) * 0.1
            scores[letter] = base_score + diversity_bonus

        return scores

    def get_next_guess(self, current_word_state: str, guessed_letters: List[str], guesses_remaining: int) -> str:
       
        current_word_state = current_word_state.lower().strip()
        self.guessed_letters = set(guessed_letters)

        # Step 1: Filter dictionary based on pattern
        self.current_dictionary = self._filter_dictionary(current_word_state, self.guessed_letters)

        print(f"[AI] Possible words remaining: {len(self.current_dictionary)}")
        if len(self.current_dictionary) <= 10:
            print(f"[AI] Candidates: {self.current_dictionary[:10]}")

        # Step 2: If only one candidate remains, pick next unguessed letter
        if len(self.current_dictionary) == 1:
            word = self.current_dictionary[0]
            for letter in word:
                if letter not in self.guessed_letters:
                    print(f"[AI] Only one word left → guessing '{letter}' from '{word}'")
                    return letter

        # Step 3: Score letters based on frequency
        if self.current_dictionary:
            letter_scores = self._calculate_letter_frequencies(self.current_dictionary, self.guessed_letters)
            if letter_scores:
                best_letter = max(letter_scores, key=letter_scores.get)
                print(f"[AI] Best guess: '{best_letter}' (score: {letter_scores[best_letter]:.3f})")
                return best_letter

        # Step 4: Fallback - common letter order
        print("[AI] Using fallback strategy (common letters)")
        for letter in self.common_letters:
            if letter not in self.guessed_letters:
                return letter

        # Step 5: Last resort - any unguessed letter
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            if letter not in self.guessed_letters:
                return letter

        # Should never happen
        return 'e'



if __name__ == "__main__":
    ai = HangmanAI()

    print("=== Test 1: '__ __ __ __ __ __ ' ===")
    guess = ai.get_next_guess("__ __ __ __ __ __ ", [], 6)
    print(f"First guess: {guess}\n")

    print("=== Test 2: 'f __ i __ h t' ===")
    ai.reset()
    guess = ai.get_next_guess("f __ i __ h t", ['f', 'i', 'h', 't'], 4)
    print(f"Next guess: {guess}\n")

    print("=== Test 3: 'a i r __ o r t' ===")
    ai.reset()
    guess = ai.get_next_guess("a i r __ o r t", ['a', 'i', 'r', 'o', 't'], 5)
    print(f"Next guess: {guess}\n")

