import zstandard
import os
from pprint import pprint
from shutil import copyfile


tempDir = "./Tmp/"
inputFile = "./ReplayFiles/end.rec"

# def getHeader(path):
#     with open(path, 'rb') as fh:
#         magic_check = fh.read(4)
#         if magic_check != b'\x28\xb5\x2f\xfd':
#             return None
        
#         tempFile = tempDir + random_sting(16) + ".compressed"
#         leadingFile = open(tempFile,"wb")
#         leadingFile.write(magic_check)

#         #wait till next file
#         while data := fh.read(1):
#             if data == b'\x28':
#                 rest_magic = fh.read(3)
#                 if rest_magic == b'\xb5\x2f\xfd':
#                     #file completed
#                     leadingFile.close()
#                     return tempFile
#                 else:
#                     leadingFile.write(data)
#                     leadingFile.write(rest_magic)
#             else:
#                 leadingFile.write(data)

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