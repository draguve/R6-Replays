import zstandard
import random
import string
import os
import struct
import sys
from pprint import pprint
import mmap
from shutil import copyfile
import argparse

tempDir = "./Tmp/"

Verbose = True


maps = {
    "837214085": "Clubhouse",
    "305979357167" : "Border",
    "1460220617" : "Kanal",
    "276279025182" : "Skyscraper",
    "53627213396" : "Tower",
    "259816839773" : "Chalet",
    "355496559878" : "Bank",
    "231702797556" : "Oregon",
    "1378191338" : "Kafe Dostoyevsky",
    "88107330328" : "Villa",
    "42090092951" : "Coastline"
}

# Credit to wholivesinapineappleunderthesea for this part 
modes = {
    "2" : "MATCHMAKING_PVP_RANKED",
	"3" : "MATCHMAKING_PVE",
	"4" :"MATCHMAKING_PVE_PARTY",
	"5" : "MATCHMAKING_PVE_LONEWOLF",
	"6" : "OPERATIONS",
	"7" : "CUSTOMGAME_PVP",
	"8" : "CUSTOMGAME_PVP_DEDICATED",
	"9" : "DEV",
	"A" : "MATCHMAKING_PVP_EVENT",
	"B" : "MATCHMAKING_PVP_NEWCOMER" ,
	"C" : "MATCHMAKING_PVP_UNRANKED",
	"D" : "MATCHREPLAY",
	"E" : "PLATFORM_TOURNAMENT"
}

teams = {}

def verbose(data,end=None):
    if(Verbose):
        print(data,end=end)

def random_sting(n):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def magic_check(path):
    with open(path, 'rb') as fh:
        magic_check = fh.read(4)
        if magic_check != b'\x28\xb5\x2f\xfd':
            return False
    return True

def getHeader(path,delete=True):
    try:
        with open(path, 'rb') as fh:
            magic_check = fh.read(4)
            if magic_check != b'\x28\xb5\x2f\xfd':
                return None
            
            tempFile = tempDir + random_sting(16) + ".compressed"
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
    finally:
        if(delete):
            os.remove(path)

def extract(filename,delete = False):  
    try:
        output = tempDir + random_sting(16) + ".decompressed"
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
    return fh.read(value).decode('UTF-8')

def get_settings(fh):
    variable = get_string(fh)
    if variable == None:
        print("Failed Getting Setting")
    value = get_string(fh)
    return (variable,value)

def worldid(settings):
    teams["Map"] = maps.get(settings[1],settings[1])
    print("MAP : " + maps.get(settings[1],settings[1]),)

def round_number(settings,fh):
    overtimeround = int(get_settings(fh)[1]) +  int(settings[1])
    teams["RoundNumber"] = str(overtimeround)
    print("Round Number : " + str(overtimeround))

def match_type(settings):
    teams["MatchType"] = modes.get(settings[1],settings[1])
    print("Match Type : " + teams["MatchType"])

def teamname(setting):
    team = setting[0][-1]
    if not team in teams:
        teams[team] = {}
    teams[team]["Name"] = setting[1]

def get_player(last,fh):
    playerid = last[1]
    playerName = get_settings(fh)[1]
    team = get_settings(fh)[1]
    heroname = get_settings(fh)[1]
    alliance = get_settings(fh)[1]
    roleimage =  get_settings(fh)[1]
    rolename = get_settings(fh)[1]
    roleportrait =  get_settings(fh)[1]
    if not team in teams:
        teams[team] = {}
    if not "players" in teams[team]:
        teams[team]["players"] = []
    teams[team]["players"].append({"User" : playerName,"Operator":rolename})
    #print(playerName + " : " + rolename )
    
#MAYBE NO CLUE IF THIS IS THE LOADOUT 
def get_loadout_packet(fh,special_bytes):
    code = fh.read(2)
    code2 = fh.read(3)
    data = fh.read(7)
    verbose(convert(code + code2) + " : " + convert(data))
    if(special_bytes == code):
        verbose("7 00 bytes "+convert(fh.read(7)))
        code = fh.read(29)
        verbose(convert(code[0:2]) + " : "+convert(code[2:]))
        return False
    return True

def get_spec_packet(fh,special_byte):
    code = fh.read(2)
    if convert(code) == "62 73" or convert(code) == "61 73":
        fh.seek(-2,1)
        return False
    else:
        data = fh.read(27)
        verbose(convert(code[0:2]) + " : "+convert(data))
        return code+data

def get_unknown_bytes(fh):
    last_zero = False
    while byte := fh.read(1):
        if convert(byte) == "00" and last_zero == False:
            last_zero = True
            verbose('')
        elif convert(byte) != "00" and last_zero == True:
            last_zero = False
            verbose('')
        verbose(convert(byte),end=" ")

def getInfo(filename,delete = False):
    with open(filename, 'rb') as fh:
        if fh.read(7) != b'dissect':
            print("not dissect")
        
        verbose("number after dissect : " + convert(fh.read(2)))   
        verbose("3 bytes 00  no clue : " + convert(fh.read(3)))
        verbose("Dissect Version? : " + get_string(fh))
        verbose("4 bytes of 00 no clue : " + convert(fh.read(4)))
        special_bytes = fh.read(2)
        verbose("special? bytes :" + convert(special_bytes))
        verbose("10 bytes no clue : " + convert(fh.read(10)))

        while settings := get_settings(fh) :
            if(settings[0] == "id"):
                print("MatchID : " + settings[1])
                break
            elif(settings[0] == "playerid"):
                get_player(settings,fh)
            elif(settings[0] == "roundnumber"):
                round_number(settings,fh)
            elif settings[0] == "worldid":
                worldid(settings)
            elif settings[0] == "teamname0" or settings[0] == "teamname1":
                teamname(settings)
            elif settings[0] == "matchtype":
                match_type(settings)
            else:
                verbose("Data : "+ settings[0] + " ------  " + settings[1])
        
        verbose("24 bytes no clue : " + convert(fh.read(24)))

        pprint(teams)

        while get_loadout_packet(fh,special_bytes):
            continue

        while get_spec_packet(fh,special_bytes):
            continue

        while get_unknown_bytes(fh):
            continue

        while data := fh.read(8):
            verbose(convert(data))

    if(delete):
        os.remove(filename)


#returns the compressed file without the extra information at the end and a file for the extra information at the end 
def strip_file(file_location):
    # Reverses a binary byte-wise in an efficient manner
    #static_data = bytearray() #i have no clue if it is, but its just the end data
    compressedTemp = tempDir + random_sting(16) + ".compressed"
    staticData = compressedTemp +".static"
    extracted = None
    try:
        i=17
        copyfile(file_location,compressedTemp)
        with open(file_location,"rb") as f:
            # read-only access or you get an access-denied or need to use r+b permissions
            mm = mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
            rever = mm[::-1]

            #dont ask me, all this is cursed 
            #I have no clue how this works, it just does
            # print(convert(rever[0:8]))
            # print(convert(rever[8:8+4]))
            # print(convert(rever[12:12+5]))
            while True:
                if rever[i+3:i+4] != b"\x00":
                    break
                #static_data.extend(rever[i:i+4])
                #print(convert(rever[i:i+4]))
                i = i + 4
        with open(compressedTemp, 'rb+') as filehandle:
                filehandle.seek(-i, os.SEEK_END)
                with open(staticData, 'wb') as static:
                    while data := filehandle.read(1):
                        static.write(data)
                filehandle.seek(-i, os.SEEK_END)
                filehandle.truncate()
        extracted = compressedTemp
        
        if(extracted == None):
            print("Extraction Failed ?????")
            return (None,None)
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")

    return (extracted,staticData)

def getStaticInfo(filename,delete = False):
    with open(filename, 'rb') as fh:
        while data := fh.read(8):
            verbose("Data : " + convert(data))
    if(delete):
        os.remove(filename)

def main():
    global Verbose
    ensure_dir(tempDir)

    parser = argparse.ArgumentParser()
    parser.add_argument('ReplayFile',help="R6 replay file that needs to be examined")
    parser.add_argument('-v','--verbose', action='store_true',help="Return all the information including hexdumps")
    parser.add_argument('-x','--header',action='store_true',help="Only extract the header of the compressed file")
    parser.add_argument('-s',"--save",action='store_true',help="Save the tmp file after extraction, will only print locations of hex dumps and not print analysis")
    args = parser.parse_args()

    Verbose = args.verbose
    filename = args.ReplayFile
    if not os.path.isfile(filename):
        print("File does not exist")
        return

    if not magic_check(filename):
        print("Check file : Could not find magic")

    strippedfile,static = strip_file(filename)
    
    if args.header:
        strippedfile = getHeader(strippedfile,True)

    extracted = extract(strippedfile,True)

    if(extracted == None):
        print("Check file : Extraction Failed")
    
    if args.save:
        print("Compressed data : " + extracted)
        print("Tail Data : "+ static )
    else:
        verbose("---------------------- DECOMPRESSED ----------------------------------")
        getInfo(extracted,True)
        verbose("-----------------------END BITS --------------------------------------")
        getStaticInfo(static,True)
        
if __name__ == "__main__":
    main()