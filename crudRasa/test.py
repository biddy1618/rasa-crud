import pickle

with open('./crudRasa/static/stories.pickle', 'rb') as f:
    data = pickle.load(f)

intents = data['intentsAll']

storiesAll = data['storiesWhole']

intentsStories = []

for k, v in storiesAll.items():
    intentsStories.append(k)
    for i in v:
        intentsStories.append(i)

print(f'Intents all - len {len(intents)}, set {len(set(intents))}')
print(f'Intents stories - len {len(intentsStories)}, set {len(set(intentsStories))}')

intentsSingle = sorted(list(set(intents) - set(intentsStories)))

print(f'Intents single - {len(set(intentsSingle))}')

with open('./crudRasa/static/stories.md', 'w') as f:
    for i, intent in enumerate(intentsSingle):
        f.write(f'## story {intent}\n')
        f.write(f'* {intent}\n')
        f.write(f'  - utter_{intent}\n\n')
    
    for k, v in storiesAll.items():
        f.write(f'## story {k}_story\n')
        for sIntent in v:
            f.write(f'* {sIntent}\n')
            f.write(f'  - utter_{sIntent}\n')
        f.write(f'* {k}\n')
        f.write(f'  - utter_{k}\n\n') 