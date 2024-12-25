dict_a = {'hello': 'hello a'}
dict_b = {'hello': 'hello b'}
dict_copy = None

print dict_a
print dict_b
print dict_copy
print ""

dict_copy = dict_a
dict_copy['hello'] = 'goodbye a'
print dict_a
print dict_b
print dict_copy
print ""

dict_a = {'hello': 'hello a'}
print dict_a
print dict_b
print dict_copy
print ""
