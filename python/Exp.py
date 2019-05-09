import json

did_list = str({"did":"Th7MpTaRZVRYnPiabds81Y","verkey":"FYmoFw55GeQH7SRFa37dkx1d2dZ3zUF8ckg7wmL7ofN4","tempVerkey":null,"metadata":null})
print(did_list[0])
A = json.dumps(did_list[0])
print(A)
print(type(A))

B = json.loads(A)
print(B)
print(type(B))

steward_did = did_list[0]['did']
print(steward_did)
type(steward_did)
print(type(steward_did))

