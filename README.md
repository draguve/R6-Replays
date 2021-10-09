# How to use it as is
you need to install all the dependencies using:
`
pip install -r /path/to/requirements.txt
`
I suggest using a venv

after install the dependencies just run it with 

`
python main.py <replay_path>
`
this would give you all the information. By default it prints out all the things that it gets including bytes in hex that I dont understand,I generally just pipe that information into a file to read it separately using this command
`
python main.py <replay_path> > output.txt
`
If you want only the infomration that the script understands there is a boolean "Verbose" changing that to a False would make it so it only prints the metadata it understands. There is more information about the operators that can be obtained, if you want to make a script to extract for stats or something in the function "get_player".


currently you can use the script to get some basic information about the match using the script. matchid, datetime, Map*, round numbers, teamnames and the teamoperators and who was using them.
*: you can get the map but the map is based on the worldid and i havent mapped all the maps to their worldid's theres a dict on the top of the script of all of the maps that i have mapped.

## Understanding the file.
In the replay system each .rec file contains the information to play one round. the data is compressed with zstd But there seems to be something attached along the end of the file  (i got a hunch it might be the scoreboard after the round ends but i dont know)

you can see the magic for the zstd files in the hex and the assembly of the game binary also has a few zstd functions exported i think.
you can decompress the entire thing with any of the zstd libs
[magic1] [magic2]

### After Decompression
The first few bytes spell out "dissect" and then a version number i have a feeling this might be their magic for a serialization/deserialization lib or a parser. there are a few temp files in the main directory of the game with the same name iirc. 
The first frame of zstd also holds the meta data of the match. there are also 2 bytes stored here which seem to be important later (i called these "special bytes" in the code).
[metadata]
after the version number the system seems to store the length,then 7 0x00 bytes then then the string, we can get quite a bit of information about the match here, date-time, operators, teamnames, maps etc... there seems to be some "gmsettings" which correspond to some game mode settings but i havent figure out how they work yet. after the match id is stored starts the part where i have no clue what anyof the bytes mean. there just seems to be a pattern that i can see but i have no clue what it means. hopefully someone smarter can figure it out.

### the unknown stuff
after the metadata in the strings there seems to be a 2 byte number that keeps incrementing then 3 0x00 bytes and then 7 bytes of some information, it seems like a table of somesorts but im grasping for straws here. for example:
`
01 00 00 00 00 : 00 00 c0 0a 7e 4b 3f
02 00 00 00 00 : 00 00 ab 7f 49 a2 3f
03 00 00 00 00 : 00 80 75 c7 f0 b4 3f
04 00 00 00 00 : 00 c0 9a 2a a6 c0 3f
05 00 00 00 00 : 00 c0 ea 6b 24 c5 3f
06 00 00 00 00 : 00 c0 72 36 e4 c9 3f
07 00 00 00 00 : 00 c0 0a 65 a8 ce 3f
08 00 00 00 00 : 00 60 11 f8 c3 d1 3f
`
then when the incrementing bytes reach as specific number, the ones i called "special bytes" it starts a 29 byte sequence that also seems to have somesort of pattern. What that looks like when the "special" bytes are 0x3c 0x10:
`
3b 10 00 00 00 : b0 2a 72 cb a5 62 40
3c 10 00 00 00 : b0 5a 9d df a6 62 40
7 00 bytes 00 00 00 00 00 00 00
00 00 : 00 00 00 d5 08 00 00 01 d0 0f 00 94 16 12 00 ff ff ff ff 44 43 32 97 01 00 00 00
3c 10 : 00 00 00 7f 38 00 00 03 10 07 00 38 b0 78 00 ff ff ff ff 44 43 32 97 01 00 00 00
3c 10 : 00 00 00 5a 38 00 00 04 c0 3f 00 a5 0d 09 00 ff ff ff ff 44 43 32 97 01 00 00 00
3c 10 : 00 00 00 e7 37 00 00 0b 10 6d 00 c1 83 07 00 ff ff ff ff 44 43 32 97 01 00 00 00
3c 10 : 00 00 00 f1 3c 00 00 0c 80 34 00 c0 35 79 00 ff ff ff ff 44 43 32 97 01 00 00 00
3c 10 : 00 00 00 2b 39 00 00 11 30 49 00 6c 8f 0e 00 ff ff ff ff 44 43 32 97 01 00 00 00
3c 10 : 00 00 00 37 36 00 00 12 c0 3e 00 01 ab 7a 00 ff ff ff ff 44 43 32 97 01 00 00 00
3c 10 : 00 00 00 19 3d 00 00 14 50 47 00 51 f9 73 00 ff ff ff ff 44 43 32 97 01 00 00 00
3c 10 : 00 00 00 91 3c 00 00 15 e0 66 00 52 ad 11 00 ff ff ff ff 44 43 32 97 01 00 00 00
`

after that ends there is what i feel individual packets of data telling us about the movement of the entities in the game but i couldn't figure out how they're structured. they always seem to start with some "id" byte that tells us about what the "packet" is and then 3 bytes that specify the entity but again i have no clue how it all works.

`
00 00 
64 
00 00 00 00 00 00 00 
62 73 85 fe 77 8d e1 4d 43 
00 00 00 00 00 00 00 00 00 00 00 
8c a3 3d 41 eb 13 88 41 77 61 3a c0 
00 00 00 00 00 00 00 00 00 00 00 00 
9d 06 7f 3f a8 7e b2 3d 01 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
01 
`

For example here the "62 73 85 fe" is repeated multiple times and the "e1 4d 43" seems to be a id for an entity. sometimes preamble becomes "60 73 85 fe" but it repeats a lot. other things the repeat are also [hex] [hex2]