# exp = "(p->q)->(~r^q)"

# stack = []

# for i in exp:
#   ch = i
#   if ch != ')':
#     stack.append(ch)
#     continue
#   stack.append(ch)
#   break

    
# evaluates logicall expression
def evaluate(stack):
    ans = []    
    for i in range(len(stack)):
# put the i in ans if it is a lowercase character
        
        if stack[i] == '-' and stack[i+1] == '>':
            ans.append('#')
            continue
        else:
            
            ans.append(stack[i])
        
    
    
    return '~' + ''.join(ans)
    

print(evaluate("(p->q)->(~r^q)"))


         
        