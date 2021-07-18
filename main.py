import zstandard
from pprint import pprint
from bitstring import ConstBitStream

path = "./ReplayFiles/Match-2021-07-18_21-22-12-113/Match-2021-07-18_21-22-12-113-R01.rec"


def dump(obj):
    for attr in dir(obj):
        if attr.__str__()[0] == '_':
            continue
        print("obj.%s = %r" % (attr, getattr(obj, attr)))


s = ConstBitStream(filename=path)
found = list(s.findall('0x28b52ffd', bytealigned=True))
if found:
    found = found[1:]
    pprint(found)

found.append(-1)

with open(path, 'rb') as fh:
    for item in found:
        dctx = zstandard.ZstdDecompressor()
        reader = dctx.stream_reader(fh)
        while True:
            if fh.tell() < item or item == -1:
                break
            chunk = reader.read(16384)
            if not chunk:
                break
