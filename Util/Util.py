#& Imports
import random

#& Random ID Generator
c = "abcdefghijklmnopqrstuvwxyz"
def get_random_id():
    r = ""
    for _ in range(30):
        r += c[random.randrange(0, len(c))]
    return r
