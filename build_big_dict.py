import pymorphy3
import os

def build_from_sys():
    """
    Генерирует частотный словарь на основе системной базы PyMorphy3.
    Создает файл corpus.txt, где каждому слову присваивается начальный вес 1.
    """
    try:
        morph = pymorphy3.MorphAnalyzer()

        output_dir = 'data'
        output_path = os.path.join(output_dir, 'corpus.txt')
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        k = 0
        with open(output_path, 'w', encoding = 'utf-8') as f:
            for w in morph.dictionary.words.keys():
                if len(w) > 1:
                    f.write(f"{w.lower()} 1\n")
                    k += 1

        print(f"В {output_path} сохранено {k} уникальных слов")

    except Exception as e:
        print(f"Ошибка при сборке словаря: {e}")

if __name__ == "__main__":
    build_from_sys()
