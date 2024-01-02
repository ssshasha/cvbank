
#  4.)) ANS
#------------------
# must pass first parameter as list


def item_count(x,y):
    count=0
    for i in x:
        if i == int(y):
            count += 1
    return count

print(item_count([1,2,3,1,2,5,4,6],2))




# 5th question is not there and 6th question i did not understsnt   



    

#  7.)) ANS
#----------------
#must provide first parameter as list

def combine(x,y):
    if type(x) == type(y):
        x.extend(y)
        return x
        
    else:
        x.append(y)
        return x

print(combine([1,2,1,2],(1,2,3)))
print(combine([1,2,1,2],'r'))
print(combine([1,2,1,2],[1,2,3]))




# 8.))ANS
#-------------

def type_and_length(obj):
    data=[]
    ty=type(obj)

    try:
        le=len(obj)
    except:
        le=None
    data.append(obj)
    data.append(ty)
    data.append(le)

    return tuple(data)


for obj in (1,"hi",1.5, True, [1,2,3],(4,5)):
    print(type_and_length(obj))
            



#  9.)))
# -----------------


def reverse_zip(zip_obj):
    return list(zip_obj)

zip_obj=zip([5,6],[9,10],["a","b"])

print(reverse_zip(zip_obj))



# 10.))
#-------------------

def indicies(l,x):
    y=[]
    if x in l:
        for i,j in enumerate(l):
            if j == x:
                
                y.append(i)
        return y    
            

    else:
        return []

print(indicies([1,2,3,2,3,6,2],2))





# 11. )))
#--------------------------

def return_value(dic,key):
    if key in dic.keys():
        return dic[key]

    else:
        return 'Key is not available in dict!!!'

dic={1:'dghd','g':'job'}
print(return_value(dic,'g'))



# 12.)))
#-----------------------






def build_book_dict(titles, pages, firsts, lasts, locations):
    d={}
    ret={}
    for i in range(len(titles)):
        d[titles[i]]={'Publisher':{'location':locations[i]},
                      'Author':{'last':lasts[i],'Firsts':firsts[i]},
                      'pages':pages[i]}

        ret.update(d)
    return ret
        
        





titles = ["Harry Potter", "Fear and Lothing in Las Vegas"]
pages = [200, 350]
firsts = ["J.K.", "Hunter"]
lasts = ["Rowling", "Thompson"]
locations = ["NYC", "Aspen"]



print( build_book_dict(titles, pages, firsts, lasts, locations))




# 13.)))
#---------------

Ans:---> d


# 14.)
#-----------



def divisible_by_3(list_item):
    x=[]

    for i in list_item:
        if i%3 == 0:
            x.append(i*2)
    return x


print(divisible_by_3([1,2,3,6,4,5,9,12,24,6]))

 


# 15 and 16 question is not there



# 17.)
#---------------



def final_element(nested_list):

    return nested_list[-1][-1]


nested = [[1,2,3],[4,5,6],[7,8,"a",4]]
print(final_element(nested))

'''

#  18.)
#-------------



def apply_functions(list_of_objs, list_of_funcs):
    
    z=[]
    x=[]
    for i in list_of_objs:
        for j in list_of_funcs:
            z.append(j(i))
             
        z=tuple(z)
        x.append(z)
        z=[]
        
    return x


objs = [(1,2),[1,3,4,5,6,7],[0]]
funcs = [len,sum]
print(apply_functions(objs, funcs))


            





































    






















