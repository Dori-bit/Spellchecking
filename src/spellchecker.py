import os
import re
import pymorphy3
from collections import Counter

class SpellChecker:
    """
    Класс для проверки орфографии и предложения исправлений.
    Использует алгоритм Питера Норвига и морфологический анализатор PyMorphy3.
    """
    def __init__(self, dict_path):
        self.morph = pymorphy3.MorphAnalyzer()
        self.w_k = self.load_data(dict_path)
        self.tot_w = sum(self.w_k.values())
        print(f"Загрузили {len(self.w_k)} уникальных слов")

    def load_data(self, path):
        """Загружает частотный словарь из текстового файла."""
        d = Counter()
        pos_paths = [path, os.path.join('data', os.path.basename(path))]
        
        targ_path = None
        for p in pos_paths:
            if os.path.exists(p):
                targ_path = p
                break
        
        if not targ_path:
            print(f"Файл {path} не найден!")
            return d
        
        try:
            with open(targ_path, 'r', encoding = 'utf-8') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        word = parts[0].lower()
                        try:
                            freq = int(parts[1])
                            d[word] = freq
                        except ValueError:
                            continue
            print("Словарь успешно инициализирован")
        except Exception as e:
            print(f"Ошибка при чтении словаря: {e}")
        return d

    def P(self, word):
        """Вычисляет вероятность слова на основе сглаживания Лапласа."""
        return (self.w_k.get(word, 0) + 0.1) / (self.tot_w + 1)

    def is_cor(self, word):
        """Проверяет, существует ли слово в словаре или в базе морфологии."""
        return word in self.w_k or self.morph.word_is_known(word)

    def edits1(self, word):
        """Генерирует все возможные правки на расстоянии 1."""
        letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def get_cand(self, word):
        """Возвращает 3 наиболее вероятных исправления для слова."""

        e1 = {w for w in self.edits1(word) if self.is_cor(w)}
        if e1:
            return sorted(list(e1), key=lambda x: (self.P(x), x), reverse = True)[:3] 

        e2 = {w2 for w1 in self.edits1(word) for w2 in self.edits1(w1) if self.is_cor(w2)}
        if e2:
            return sorted(list(e2), key=lambda x: (self.P(x), x), reverse = True)[:3]

        return [word]

if __name__ == "__main__":
    path = 'corpus.txt' 
    checker = SpellChecker(path)

    print("Введите слово для проверки или 'exit' для выхода")
    
    while True:
        try:
            raw_input = input("> ").strip()
            
            clean_input = raw_input.lower().replace('.', '').strip()
            if not raw_input or clean_input == 'exit':
                break
            
            words = re.findall(r'[а-яёА-ЯЁ\-]+', raw_input)
            
            for w in words:
                w_l = w.lower()
                if checker.is_cor(w_l):
                    print(f"{w} — корректно")
                else:
                    recs = checker.get_cand(w_l)
                    print(f"{w} — опечатка. Возможно вы имели в виду: {', '.join(recs)}")
                    
        except KeyboardInterrupt:
            break
