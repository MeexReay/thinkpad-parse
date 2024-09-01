import ollama

thinkpads_content = "\n".join(open("thinkpads.txt", "r").readlines()[:10])
prompt = """
Подбери самый дешевый ноутбук подходящий по предпочтениям из данных
Предпочтения:
  Хороший аккумулятор
  Среднее кол-во памяти (6+ гб)
  Тип диска - SSD
  Вместительность диска - минимум 250 гб
  Хороший процессор
  Видеокарта не важна
  Цена: минимально возможная
  Клавиатура и тачпад: в нормальном состоянии
  USB порты: минимум 2
  Тип системы: не важен
  Монитор: без требования в ремонте
  Зарядное устройство: имеется
Данные:
"""+thinkpads_content

ollama.pull("llama3.1")

stream = ollama.generate(
    model='llama3.1',
    prompt=prompt,
    stream=True,
)

for chunk in stream:
  print(chunk['response'], end='', flush=True)
print()