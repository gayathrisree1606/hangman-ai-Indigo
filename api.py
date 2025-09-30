from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from ai_engine import HangmanAI

# Initialize AI
ai = HangmanAI("words.txt")

# FastAPI app
app = FastAPI(title="Hangman AI Solver")



# Input model
class GuessRequest(BaseModel):
    currentWordState: str
    guessedLetters: List[str]
    guessesRemaining: int

# Output model
class GuessResponse(BaseModel):
    nextGuess: str



@app.post("/guess", response_model=GuessResponse)
def get_guess(request: GuessRequest):
    next_letter = ai.get_next_guess(
        current_word_state=request.currentWordState,
        guessed_letters=request.guessedLetters,
        guesses_remaining=request.guessesRemaining
    )
    return {"nextGuess": next_letter}

@app.post("/reset")
def reset_ai():
    ai.reset()
    return {"message": "AI state reset"}

@app.get("/health")
def health_check():
    return {"status": "OK"}


@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hangman AI</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            input, button { padding: 10px; font-size: 16px; margin: 5px; }
        </style>
    </head>
    <body>
        <h1>Hangman AI Solver</h1>
        <p>Enter the current word state (use underscores for blanks, e.g., "_ _ e _ a n"):</p>
        <input type="text" id="currentWordState" size="20">
        <p>Guessed letters (comma separated):</p>
        <input type="text" id="guessedLetters" size="20">
        <p>Guesses remaining:</p>
        <input type="number" id="guessesRemaining" value="6" min="1" max="26">
        <br>
        <button onclick="getNextGuess()">Get Next Guess</button>
        <h2>AI Guess: <span id="nextGuess">-</span></h2>

        <script>
            async function getNextGuess() {
                const state = document.getElementById("currentWordState").value;
                const guessed = document.getElementById("guessedLetters").value.split(',').map(s => s.trim()).filter(s=>s);
                const remaining = parseInt(document.getElementById("guessesRemaining").value);

                const response = await fetch("/guess", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        currentWordState: state,
                        guessedLetters: guessed,
                        guessesRemaining: remaining
                    })
                });

                const data = await response.json();
                document.getElementById("nextGuess").innerText = data.nextGuess;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)






