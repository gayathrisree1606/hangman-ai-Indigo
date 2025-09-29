import requests

url = "http://127.0.0.1:8000/guess"
data = {
    "currentWordState": "__ __ e __ a n",
    "guessedLetters": ["e", "a", "n"],
    "guessesRemaining": 4
}

response = requests.post(url, json=data)
print(response.json())


