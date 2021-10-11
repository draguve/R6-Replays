import zstandard
import os
from pprint import pprint
from shutil import copyfile


tempDir = "./Tmp/"
inputFile = "./ReplayFiles/end.rec"

def extract_till_success(path):
    removed_bytes = 0
    Success = False
    filename = tempDir+"end.rec.working"
    copyfile(path,filename)
    while not Success:
        try:
            output = tempDir + "end.rec.decompressed"
            stream = open(filename, "rb")
            f = open(output , "wb")
            dctx = zstandard.ZstdDecompressor()
            reader = dctx.stream_reader(stream)
            while True:
                chunk = reader.read(16384)
                if not chunk:
                    break
                f.write(chunk)
            f.close()
            stream.close()
            Success = True
            print("we removed " + str(removed_bytes) + " from the end")
        except zstandard.ZstdError:
            f.close()
            stream.close()
            with open(filename, 'rb+') as filehandle:
                filehandle.seek(-1, os.SEEK_END)
                filehandle.truncate()
                removed_bytes += 1    

if __name__ == "__main__":
    extract_till_success(inputFile)