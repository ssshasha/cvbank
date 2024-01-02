string=input()


def string_expansion(string):
    n=0
    i=2
    ret_str=''
    if string:
        while n <= len(string):
            s=string[n]
            ret_str += 2*s*n+s*2
            n +=2
        return ret_str
        
        
    else:
        return 'string is not provided !!'

z=string_expansion(string)
print(z)
