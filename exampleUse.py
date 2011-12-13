import pyOnJs

class Info:
    _json = ["uptime","usage"]
    def __init__(self, up, us):
        self.uptime = up
        self.usage = us

class AppStatus:
    _json = ["name", "hits"]
    def __init__(self, name, hits):
        self.name = name
        self.hits = hits
    
class Status(pyOnJs.PyOnJs):
    _json = ["info","status"]
    _jsonc = {"info":Info, "status":[list,AppStatus]}
    def __init__(self, name):
        self.info = Info(name,0)
        self.status = []

    def setStatus(self, name, hits):
        if [x for x in self.status if x.name==name]:
            [x for x in self.status if x.name==name][0].hits = hits
        self.status.append(AppStatus(name,hits))
        self.info.usage+=hits

s = Status("foo")
s.setStatus("a1",10)
s.setStatus("a2",22)
s.setStatus("a2",33)

json = s.dumps()
print(json)

s2 = Status.loads(json)

print(s.info.usage == s2.info.usage)
