from thethingsio.tools import ThingWriter
from random import randrange

writer = ThingWriter('<< your thing token >>')

cities = [
    None,
    {'long': 2.1685, 'lat': 41.3818},  # Barcelona
    (-73.935242, 40.730610),  # New York City
    (-0.076132, 51.508530),  # London
    (55.296249, 25.276987),  # Dubai
]

for _ in range(0, 50):
    writer.add('demo_resources', randrange(0, 9), cities[randrange(0, 4)])

print 'Writing %d values...' % len(writer)
writer.flush()
