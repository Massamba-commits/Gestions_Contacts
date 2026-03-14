import random
import string


def generer_cle():
    groupes = []
    for _ in range(5):
        groupe = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        groupes.append(groupe)
    return '-'.join(groupes)


for i in range(5):
    print(generer_cle())
