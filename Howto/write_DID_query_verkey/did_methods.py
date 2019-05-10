
def process_did_list(did_list):

    # did_list = '[{"did":"Th7MpTaRZVRYnPiabds81Y","verkey":"FYmoFw55GeQH7SRFa37dkx1d2dZ3zUF8ckg7wmL7ofN4","tempVerkey":null,"metadata":null},{"did":"7ej73V5MAnHRNwYTzkQHMB","verkey":"4dEZKQm2Q9V4FWr4xBPnkiX9TmQjwfZdKm6BEkDyqwoW","tempVerkey":null,"metadata":null}]'

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
            
    return dids



