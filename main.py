import zstandard
import random
import string
import os
import struct

path = "./ReplayFiles/Match-2021-09-30_00-01-50-55-R01.rec"
location = "./Outputs/"
temp = "./Tmp/"

Verbose = True

def verbose(data):
    if(Verbose):
        print(data)

def random_sting(n):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def getHeader():
    ensure_dir(location)
    ensure_dir(temp)

    with open(path, 'rb') as fh:
        magic_check = fh.read(4)
        if magic_check != b'\x28\xb5\x2f\xfd':
            return None
        
        tempFile = temp + random_sting(8)
        leadingFile = open(tempFile,"wb")
        leadingFile.write(magic_check)

        #wait till next file
        while data := fh.read(1):
            if data == b'\x28':
                rest_magic = fh.read(3)
                if rest_magic == b'\xb5\x2f\xfd':
                    #file completed
                    leadingFile.close()
                    return tempFile
                else:
                    leadingFile.write(data)
                    leadingFile.write(rest_magic)
            else:
                leadingFile.write(data)

def extract(filename,output,delete = False):  
    try:
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
        return output
    except zstandard.ZstdError:
        print("location?= " + str(stream.tell()))
        print("filename = " + output)
        # TODO: it kindof crashes here on the last stream. fails to find the zstd frame
        f.close()
        stream.close()
        return None
    finally:
        if(delete):
            os.remove(filename)

def convert(data):
    return " ".join("{:02x}".format(x) for x in data)

def get_string(fh):
    #value = struct.unpack('B', fh.read(1)[0])[0]
    value = struct.unpack('B', fh.read(1))[0]
    if(fh.read(7) != b'\x00\x00\x00\x00\x00\x00\x00'):
        print("String Check Failed")
        return None
    return fh.read(value).decode('ASCII')

def get_settings(fh):
    variable = get_string(fh)
    if variable == None:
        print("Failed Getting Setting")
    value = get_string(fh)
    return (variable,value)

def get_player(last,fh):
    playerid = last[1]
    playerName = get_settings(fh)[1]
    team = get_settings(fh)[1]
    heroname = get_settings(fh)[1]
    alliance = get_settings(fh)[1]
    roleimage =  get_settings(fh)[1]
    rolename = get_settings(fh)[1]
    roleportrait =  get_settings(fh)[1]
    print(playerName + " : " + rolename )
    

def getInfo(filename):
    with open(filename, 'rb') as fh:
        if fh.read(7) != b'dissect':
            print("not dissect")
        
        verbose("number after dissect : " + convert(fh.read(2)))   
        verbose("3 bytes 00  no clue : " + convert(fh.read(3)))
        verbose("Dissect Version? : " + get_string(fh))
        verbose("16 bytes no clue : " + convert(fh.read(16)))

        while settings := get_settings(fh) :
            if(settings[0] == "id"):
                print("MatchID : " + settings[1])
                break
            elif(settings[0] == "playerid"):
                get_player(settings,fh)
            else:
                print("Data : "+ settings[0] + " ------  " + settings[1])
        
def main():
    # temp = getHeader()
    # extracted = extract(temp,location + "Test.de",True)

    getInfo(location + "Test.de")


main()