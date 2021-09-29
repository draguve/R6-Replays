import zstandard
import random
import string
import os
import sys

path = "./ReplayFiles/Match-2021-07-22_22-54-32-197-R02.rec"
location = "./Outputs/"
temp = "./Tmp/"


def random_sting(n):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def main():
    ensure_dir(location)
    ensure_dir(temp)

    streams = []
    names = []
    with open(path, 'rb') as fh:
        index = -1
        writers = []

        while data := fh.read(1):
            if data == b'\x28':
                rest_magic = fh.read(3)
                if rest_magic == b'\xb5\x2f\xfd':
                    index += 1
                    name = random_sting(20)
                    f = open(temp + name, "wb")
                    streams.append(f)
                    names.append(name)
                    streams[index].write(data)
                    streams[index].write(rest_magic)
                else:
                    streams[index].write(data)
                    streams[index].write(rest_magic)
            else:
                streams[index].write(data)

    streams = [stream.close() for stream in streams]

    i = 0
    for name in names:
        try:
            stream = open(temp + name, "rb")
            f = open(location + "stream_" + str(i) + ".decompressed", "wb")
            dctx = zstandard.ZstdDecompressor()
            reader = dctx.stream_reader(stream)
            while True:
                print("t = " + str(reader.tell()))
                chunk = reader.read(16384)
                if not chunk:
                    break
                f.write(chunk)
            i += 1
            f.close()
            stream.close()
        except zstandard.ZstdError:
            print("location?= " + str(stream.tell()))
            print("filename = " + name)
            # TODO: it kindof crashes here on the last stream. fails to find the zstd frame
            f.close()
            stream.close()
        finally:
            #os.remove(temp + name)
            pass


if __name__ == "__main__":
    main()
