data =""".............
...._........
.._/A\_..._..
./B\_/D\_/F\.
.\_/C\_/E\_/.
...\_/G\_/...
.....\_/.....
............."""

data = list(data)
data.reverse()
data = ''.join(data)
print(data , '\n')
data = data.split('\n' )

edit_list = []
y = 0
for h in data:
    data[y] += '\n'
    y = y + 1
    x = 0
    for w in h:
        x = x + 1
        if w.isalpha():
            print(w , x , y)
            edit_list.append( [w , x , y])

def swap(data, my_x , my_y , sinbol ):
    n = 0
    y= 0
    for h in data:
        y = y + 1
        x = 0
        for w in h:
            x = x + 1
            if x ==  my_x and y == my_y:
                return n
            n += 1

print( swap(data , 7 , 3 , '_') )

data = ''.join(data)

