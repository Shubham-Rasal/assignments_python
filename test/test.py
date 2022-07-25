import math
dict={}

#rsa cypher
def rsa_cypher(plaintext,e,n):
    ciphertext=pow(plaintext,e)
    ciphertext=math.fmod(ciphertext,n)
    return ciphertext
    

for i in range(1,11):
    dict[i]=rsa_cypher(i,3,11)

print(dict)