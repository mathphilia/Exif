from Exif_modify import Exif_modify, TAGS, GPSTAGS
import os, sys
from PIL import Image, UnidentifiedImageError

def _bytes2Exifdata(content, tag_type, endian):
    signed_long = lambda n: -(n ^ 0xffffffff) - 1 if n & 0x80000000 else n
    if tag_type in (1, 3, 4):
        return int.from_bytes(content, endian)
    elif tag_type == 2:
        return content.decode('ASCII')
    elif tag_type == 5:
        numerator = int.from_bytes(content[:4], endian)
        denominator = int.from_bytes(content[4:], endian)
        return numerator / denominator
    elif tag_type == 7:
        return content
    elif tag_type == 9:
        return signed_long(int.from_bytes(content, endian))
    elif tag_type == 10:
        numerator = signed_long(int.from_bytes(content[:4], endian))
        denominator = signed_long(int.from_bytes(content[4:], endian))
        return numerator / denominator
    else:
        raise ValueError('unknown tag type: %d' % tag_type)


def _getIFDdata(data, index, endian, TAGS_dic):
    type_size = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 9: 4, 10: 8}
    IFDdata = {}
    Ntags = int.from_bytes(data[index:index + 2], endian)
    index += 2
    for _ in range(Ntags):
        tag = int.from_bytes(data[index:index + 2], endian)
        tag_type = int.from_bytes(data[index + 2:index + 4], endian)
        size = type_size[tag_type]
        length = int.from_bytes(data[index + 4:index + 8], endian)
        if size * length <= 4:
            address = index + 8
        else:
            address = int.from_bytes(data[index + 8:index + 12], endian)
        value = tuple(_bytes2Exifdata(data[address + size * i:address + size * (i + 1)], tag_type, endian)\
                for i in range(length))
        if tag_type == 2:
            assert value[-1] == '\x00'
            IFDdata[TAGS_dic[tag]] = ''.join(value[:-1])
        elif tag_type == 7:
            IFDdata[TAGS_dic[tag]] = b''.join(value)
        elif length == 1:
            IFDdata[TAGS_dic[tag]] = value[0]
        else:
            IFDdata[TAGS_dic[tag]] = value
        index += 12
    index = int.from_bytes(data[index:index + 4], endian)
    return IFDdata, index


def getExif(path, verbose = False):
    with open(path, 'rb') as f:
        data = f.read()
    if 2 <= data.count(b'Exif\x00\x00MM\x00*') + data.count(b'Exif\x00\x00II*\x00'):
        raise ValueError('There are too many Exif')
    try:
        if b'Exif\x00\x00MM\x00*' in data:
            data = data[data.index(b'Exif\x00\x00MM\x00*') + 6:]
            endian = 'big'
        else:
            data = data[data.index(b'Exif\x00\x00II*\x00') + 6:]
            endian = 'little'
        index = 0
    except ValueError:
        raise ValueError('There is no Exif')
    result = {'endian': endian}
    index = int.from_bytes(data[index + 4:index + 8], endian)
    result['0th IFD'], index = _getIFDdata(data, index, endian, TAGS)
    if index:
        result['1st IFD'], index = _getIFDdata(data, index, endian, TAGS)
        if verbose and index:
            print('-', 'subsequent IFD to the 1st IFD is at index %d' % index)
        thumbnail_index = result['1st IFD']['JpegIFOffset']
        thumbnail_size = result['1st IFD']['JpegIFByteCount']
        thumbnail = data[thumbnail_index:thumbnail_index + thumbnail_size]
        if not os.path.exists('thumbnail.jpg') or\
                input('Can I overwrite thumbnail in `thumbnail.jpg`? [y/N] ').lower() == 'y':
            with open('thumbnail.jpg', 'wb') as f:
                f.write(thumbnail)
        if 'ExifInteroperabilityOffset' in result['1st IFD']:
            # What is an Interoperability IFD? I don't know!
            result['Interoperability IFD'], index = _getIFDdata(
                    data, result['1st IFD'].pop('ExifInteroperabilityOffset'), endian, TAGS
                    )
            if verbose and index:
                print('-', 'subsequent IFD to the Interoperability IFD is at index %d' % index)
    if 'ExifOffset' in result['0th IFD']:
        result['Exif IFD'], index = _getIFDdata(data, result['0th IFD'].pop('ExifOffset'), endian, TAGS)
        if verbose and index:
            print('-', 'subsequent IFD to the Exif IFD is at index %d' % index)
    if 'GPSInfo' in result['0th IFD']:
        result['GPS IFD'], index = _getIFDdata(data, result['0th IFD'].pop('GPSInfo'), endian, GPSTAGS)
        if verbose and index:
            print('-', 'subsequent IFD to the GPS IFD is at index %d' % index)
    return Exif_modify(result)


if __name__ == '__main__':
    path = sys.argv[1]
    Exif = getExif(path)
    try:
        im = Image.open(path)
        info = im.info
        info['exif'] = Exif
        image_data = info
    except UnidentifiedImageError:
        image_data = {'exif': Exif}
    for key1 in image_data:
        print('-' * 10, key1, '-' * 10)
        if not isinstance(image_data[key1], dict):
            print(image_data[key1])
            print()
            continue
        for key2 in image_data[key1]:
            if not isinstance(image_data[key1][key2], dict):
                print(f'{key2}: {image_data[key1][key2]}')
                print()
                continue
            print(f'<%s>' % key2)
            for key3 in image_data[key1][key2]:
                print(f'    {key3}: {image_data[key1][key2][key3]}')
            print()