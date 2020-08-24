import json

p2t = {}

class NotInCorrectRange(Exception):
    pass


def force_to_throttle(power):
    with open('parca_kodlar/t200.json', 'r') as j:
        sozluk = json.load(j)

    if sozluk.get(str(power)):
        return (sozluk.get(str(power)) - 1500) / 400 + 0

    p_key = None
    l_key = None
    # sozluk.keys() küçükten büyüğe sıralı olmalı
    for key in sozluk.keys():
        key = int(key)
        if power > key:
            p_key = key
        else:
            l_key = key
            break

    p_value = sozluk.get(str(p_key))
    l_value = sozluk.get(str(l_key))
    o_value = (l_value - p_value) / (int(l_key) - int(p_key)) * (power - p_key) + p_value
    return (o_value - 1500) / 400 + 0


def power_to_throttle(power: int):
    if not -100 <= power <= 100:
        raise NotInCorrectRange("Power must be between -100 and 100.")
    power = str(power)
    global p2t
    if not p2t:
        with open('parca_kodlar/p2t.json', 'r') as j:
            p2t = json.load(j)
    return p2t[power]


if __name__ == '__main__':
    # d = {}
    # for i in range(-100, 101):
    #     d[i] = round(force_to_throttle(i), 3)
    # print(d)
    # with open('parca_kodlar/p2t.json', 'w') as f:
    #     json.dump(d, f)

    for i in range(-100, 101):
        if round(force_to_throttle(i), 3) != round(power_to_throttle(i), 3):
            print(i)
