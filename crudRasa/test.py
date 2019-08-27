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

intentsSingle = sorted(list(set(intentsStories) - set(intents)))

print(f'Intents single - {len(set(intentsSingle))}')

print(intentsSingle)
print('guide-forte-cards-cardissue' in intents)