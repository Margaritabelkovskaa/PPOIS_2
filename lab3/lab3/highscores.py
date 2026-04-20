import json
import os
from datetime import datetime

class HighScores:
    def __init__(self, filename='highscores.json'):
        self.filename = filename
        self.scores = []
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.scores = json.load(f)
            except:
                self.init_default_scores()
        else:
            self.init_default_scores()

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=2)

    def add_score(self, name, score):
        self.scores.append({"name": name, "score": score, "date": datetime.now().strftime('%Y-%m-%d')})
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:10]
        self.save()

    def is_high_score(self, score):
        return len(self.scores) < 10 or score > self.scores[-1]['score']

    def get_scores(self):
        return self.scores