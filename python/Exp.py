import json

def process_did_list(did_list):

    A = did_list.count('did')
    i = did_list.find('{')
    j = did_list.find('}')

    # Initiate list for storing existing dids:
    dids = [] 
    dids.append([])

    if A > 1:
        for iter in range(A):

            dids[0].append(did_list[i:j+1]) 
            i = did_list.find('{',j+1)
            j = did_list.find('}',j+1)


    print(dids)
# print(A)
# print(type(A))

# B = json.loads(A)
# print(B)
# print(type(B))

# steward_did = did_list[0]['did']
# print(steward_did)
# type(steward_did)
# print(type(steward_did))

