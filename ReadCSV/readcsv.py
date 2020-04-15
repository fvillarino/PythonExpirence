import csv

def read_csv_one_field(filepath):
    
    with open("TBSH/" + filepath, encoding = "ISO-8859-1") as csvfile:
        list_values = []
        reader = csv.DictReader(csvfile)
        for row in reader:
            list_values.append(row['mat_code'])
        return list_values

def read_csv(filepath):
    with open("TBSH/" + filepath) as csvfile:
        list_values = []
        reader = csv.DictReader(csvfile)
        list_values = list(reader)
        return list_values

def list_duplicates(seq):
  seen = set()
  seen_add = seen.add
  # adds all elements it doesn't know yet to seen and all other to seen_twice
  seen_twice = set( x for x in seq if x in seen or seen_add(x) )
  # turn the set into a list (as requested)
  return list( seen_twice )


mats_list = read_csv_one_field('mats.csv')
print('Mats -> Total values: ', len(mats_list))

cons_list = read_csv_one_field('cons.csv')
print('Cons -> Total values: ', len(cons_list))

#Listas unicas
mats_set = set(mats_list)
print('Mats Uniques -> Total values: ', len(mats_set))

cons_set = set(cons_list)
print('Cons Uniques materials -> Total values: ', len(cons_list))

mats_cons = mats_set.intersection(cons_set)
print('Intersection -> Mats in Cons:', len(mats_cons))

mats_not_cons = mats_set.difference(cons_set)
print('Difference -> Cons not mats:', len(mats_not_cons))

print('List materials not in cons:')
print(mats_not_cons)

prog_mats_list = read_csv_one_field('prog.csv')
print('Prog -> Total values: ', len(prog_mats_list))

prog_mats_set = set(prog_mats_list)
print('Prog mats Uniques -> Total values: ', len(prog_mats_set))

prog_mats_inter = prog_mats_set.intersection(mats_set)
print('Intersection -> Mats in Prog:', len(prog_mats_inter))
#print(prog_mats_inter)

prog_mats_diff = prog_mats_set.difference(mats_set) 
print('Difference -> Mats in Prog:', len(prog_mats_diff))
#print(prog_mats_diff)

prog_mats_faltantes = read_csv_one_field('mats_faltantes.csv')
print('Materiales faltantes -> count: ', len(prog_mats_faltantes))

#for material in mats_cons:
#    mats_list.index()

#aflgo