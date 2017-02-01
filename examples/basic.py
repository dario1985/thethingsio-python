import thethingsio as ttio

client = ttio.Client()

res = client.subscribe('/things/<< your thing token >>')

print "response: ", res.data
for data in res.stream:
    print "new value:", data
