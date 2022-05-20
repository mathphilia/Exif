from PIL.ExifTags import TAGS, GPSTAGS
TAGS[0x9214] = 'SubjectArea'

TAGS_value = {
    0x0103: {1: 'non-compressed', 6: 'JPEG compression'},
    0x0106: {2: 'RGB', 6: 'YCbCr'},
    0x0112: {
        1: 'no rotation', 2: 'horizontally flipped', 3: '180ﾟ right rotated', 4: 'vertically flipped',
        5: '90ﾟ right rotated and horizontally flipped', 6: '90ﾟ right rotated',
        7: '90ﾟ left rotated and horizontally flipped', 8: '90ﾟ left rotated'
    },
    0x011c: {1: 'chunky format', 2: 'panar format'},
    0x0212: {(2, 1): 'YCbCr 4:2:2', (2, 2): 'YCbCr 4:2:0'},
    0x0213: {1: 'centered', 2: 'co-sited'},
    0x0128: {2: 'inches', 3: 'centimeters'},
    0xa001: {1: 'sRGB', 65535: 'uncalibrated'},
    0x8822: {
        0: 'not defined', 1: 'manual', 2: 'normal program', 3:'aperture priority', 4: 'shutter priority',
        5: 'creative program', 6: 'action program', 7: 'portrait mode', 8: 'landscape mode'
    },
    0x8830: {
        0: 'unknown', 1: 'Standard Output Sensitivity', 2: 'Recommended Exposure Index', 3: 'ISO speed',
        4: 'Standard Output Sensitivity and Recommended Exposure Index',
        5: 'Standard Output Sensitivity and ISO speed', 6: 'Recommended Exposure Index and ISO speed',
        7: 'Standard Output Sensitivity, Recommended Exposure Index and ISO speed'
    },
    0x9207: {
        0: 'unknown', 1: 'average', 2: 'center weighted average', 3: 'spot', 4: 'multi spot',
        5: 'pattern', 6: 'partial', 255: 'other'
    },
    0x9208: {
        0: 'unknown', 1: 'daylight', 2: 'fluorescent', 3: 'incandescent light', 4: 'flash',
        9: 'fine weather', 10: 'cloudy weather', 11: 'shade', 12: 'daylight fluorescent',
        13: 'day white fluorescent', 14: 'cool white fluorescent', 15: 'white fluorescent',
        16: 'warm white fluorescent', 17: 'standard light A', 18: 'standard light B', 19: 'standard light C',
        20: 'D55', 21: 'D65', 22: 'D75', 23: 'D50', 24: 'ISO studio tungsten', 255: 'other'
        },
    0xa210: {2: 'inches', 3: 'centimeters'},
    0xa217: {
        1: 'not defined', 2: 'one-chip color area sensor', 3: 'two-chip color area sensor',
        4: 'three-chip color area sensor', 5: 'color sequential area sensor',
        7: 'trilinear sensor', 8: 'color sequential linear sensor',
    },
    0xa300: {
        b'\x00': 'other', b'\x01': 'scanner of transparent type', b'\x02': 'scanner of reflex type', b'\x03': 'DSC'
    },
    0xa301: {b'\x01': 'directly photographed'},
    0xa401: {0: 'normal process', 1: 'custom process'},
    0xa402: {0: 'auto exposure', 1: 'manual exposure', 2: 'auto bracket'},
    0xa403: {0: 'auto white balance', 1: 'manual white balance'},
    0xa406: {0: 'standard', 1: 'landscape', 2: 'portrait', 3: 'night scene'},
    0xa407: {0: 'none', 1: 'low gain up', 2: 'high gain up', 3: 'low gain down', 4: 'high gain down'},
    0xa408: {0: 'normal', 1: 'soft', 2: 'hard'},
    0xa409: {0: 'normal', 1: 'low saturation', 2: 'high saturation'},
    0xa40a: {0: 'normal', 1: 'soft', 2: 'hard'},
    0xa40c: {0: 'unknown', 1: 'macro', 2: 'close view', 3: 'distant view'},
    0xa460: {
        0: 'unknown', 1: 'non-composite image', 2: 'general composite image',
        3: 'composite image captured when shooting'
    },
}

GPSTAGS_value = {
    9: {'A': 'measurement in progress', 'V': 'measurement interrupted'},
    10: {'2': '2D', '3': '3D'},
    30: {0: 'measurement without differential correction', 1: 'differential correction applied'},
}

TAGS_unit = {
    0x9102: 'bpp', 0x829a: 's', 0x9206: 'm', 0x920a: 'mm', 0xa20b: 'BCPS', 0xa405: 'mm', 0xa462: 's',
    0x9400: '℃', 0x9401: '%', 0x9402: 'hPa', 0x9403: 'm', 0x9404: 'mGal', 0x9405: 'ﾟ',
}

def Exif_modify(Exif):
    IFDs = list(Exif)
    IFDs.remove('endian')
    if 'GPS TAG' in IFDs:
        IFDs.remove('GPS TAG')

    for tag_num in TAGS_value:
        tag = TAGS[tag_num]
        for IFD in IFDs:
            if tag in Exif[IFD]:
                Exif[IFD][tag] = TAGS_value[tag_num][Exif[IFD][tag]]
    for tag_num in TAGS_unit:
        tag = TAGS[tag_num]
        for IFD in IFDs:
            if tag in Exif[IFD]:
                Exif[IFD][tag] = '%d%s' % (Exif[IFD][tag], TAGS_unit[tag_num])
    if 'GPS IFD' in Exif:
        for tag_num in GPSTAGS_value:
            tag = GPSTAGS[tag_num]
            if tag in Exif['GPS IFD']:
                Exif['GPS IFD'][tag] = GPSTAGS_value[Exif['GPS IFD'][tag]]

    if 'Exif IFD' in Exif:
        if TAGS[0x9000] in Exif['Exif IFD']:# ExifVersion
            data = Exif['Exif IFD'][TAGS[0x9000]].decode()
            Exif['Exif IFD'][TAGS[0x9000]] = str(int(data[:2])) + '.' + data[2]
            if int(data[3]):
                Exif['Exif IFD'][TAGS[0x9000]] += '.' + data[3]
        if TAGS[0xa000] in Exif['Exif IFD']:# FlashPixVersion
            data = Exif['Exif IFD'][TAGS[0xa000]].decode()
            Exif['Exif IFD'][TAGS[0xa000]] = str(int(data[:2])) + '.' + data[2]
            if int(data[3]):
                Exif['Exif IFD'][TAGS[0xa000]] += '.' + data[3]
        if TAGS[0x9101] in Exif['Exif IFD']:# ComponentsConfiguration
            data = Exif['Exif IFD'][TAGS[0x9101]]
            dic = {0: '-', 1: 'Y', 2: 'Cb', 3: 'Cr', 4: 'R' ,5: 'G', 6: 'B'}
            Exif['Exif IFD'][TAGS[0x9101]] = ', '.join(dic[i] for i in data)
        if TAGS[0x9290] in Exif['Exif IFD']:# SubsecTime
            Exif['0th IFD'][TAGS[0x0132]] += '.' + Exif['Exif IFD'].pop(TAGS[0x9290])
        if TAGS[0x9291] in Exif['Exif IFD']:# SubsecTimeOriginal
            Exif['Exif IFD'][TAGS[0x9003]] += '.' + Exif['Exif IFD'].pop(TAGS[0x9291])
        if TAGS[0x9292] in Exif['Exif IFD']:# SubsecTimeDigitized
            Exif['Exif IFD'][TAGS[0x9004]] += '.' + Exif['Exif IFD'].pop(TAGS[0x9292])
        if TAGS[0x9010] in Exif['Exif IFD']:# OffsetTime
            Exif['0th IFD'][TAGS[0x0132]] += ' (' + Exif['Exif IFD'].pop(TAGS[0x9010]) + ')'
        if TAGS[0x9011] in Exif['Exif IFD']:# OffsetTimeOriginal
            Exif['Exif IFD'][TAGS[0x9003]] += ' (' + Exif['Exif IFD'].pop(TAGS[0x9011]) + ')'
        if TAGS[0x9012] in Exif['Exif IFD']:# OffsetTimeDigitized
            Exif['Exif IFD'][TAGS[0x9004]] += ' (' + Exif['Exif IFD'].pop(TAGS[0x9012]) + ')'
        if TAGS[0x9209] in Exif['Exif IFD']:# Flash
            data = Exif['Exif IFD'][TAGS[0x9209]]
            Exif['Exif IFD'][TAGS[0x9209]] = {0: 'did not fire, ', 1: 'fire, '}[data & 0x01]
            Exif['Exif IFD'][TAGS[0x9209]] += {
                0: 'no strobe return detection function, ', 4: 'strobe return light not detected, ', 
                6: 'strobe return light detected, '
            }[data & 0x06]
            Exif['Exif IFD'][TAGS[0x9209]] += {
                0: 'strobe mode unknown, ', 8: 'compulsoryflash firing, ',
                16: 'compulsory flash suppression', 24: 'autoflash mode'
            }[data & 0x18]
            Exif['Exif IFD'][TAGS[0x9209]] += {0: 'flash function present', 32: 'no flash function'}[data & 0x20]
            Exif['Exif IFD'][TAGS[0x9209]] += {
                0: 'red-eye reduction mode not exist or unknown', 1: 'red-eye reduction supported'
            }[data & 0x40]
        if TAGS[0x9214] in Exif['Exif IFD']:# SubjectArea
            data = Exif['Exif IFD'][TAGS[0x9214]]
            if len(data) == 2:
                Exif['Exif IFD'][TAGS[0x9214]] = '(x, y) = (%d, %d)' % data
            elif len(data) == 3:
                Exif['Exif IFD'][TAGS[0x9214]] = '(x, y, r) = (%d, %d, %d)' % data
            elif len(data) == 4:
                Exif['Exif IFD'][TAGS[0x9214]] = '(x, y, width, height) = (%d, %d, %d, %d)' % data
        if TAGS[0xa432] in Exif['Exif IFD']:# LensSpecification
            Exif['Exif IFD'][TAGS[0xa432]] = '%s~%smm, f/%s~%s' % Exif['Exif IFD'][TAGS[0xa432]]
    if 'GPS IFD' in Exif:
        if GPSTAGS[1] in Exif['GPS IFD']:# GPSLatitudeRef
            dd, mm, ss = Exif['GPS IFD'][GPSTAGS[2]]
            dd = str(int(dd))
            if mm == int(mm):
                mm, ss = str(int(mm)), str(ss)
            else:
                mm, ss = str(mm), ''
            Exif['GPS IFD'][GPSTAGS[2]] = '%sﾟ %s\' %s" %s' % (dd, mm, ss, Exif['GPS IFD'].pop(GPSTAGS[1]))
        if GPSTAGS[3] in Exif['GPS IFD']:# GPSLongitudeRef
            dd, mm, ss = Exif['GPS IFD'][GPSTAGS[4]]
            dd = str(int(dd))
            if mm == int(mm):
                mm, ss = str(int(mm)), str(ss)
            else:
                mm, ss = str(mm), ''
            Exif['GPS IFD'][GPSTAGS[4]] = '%sﾟ %s\' %s" %s' % (dd, mm, ss, Exif['GPS IFD'].pop(GPSTAGS[3]))
        if GPSTAGS[5] in Exif['GPS IFD']:# GPSAltitudeRef
            GPSAltitudeRef = Exif['GPS IFD'].pop(GPSTAGS[5])
            if GPSAltitudeRef == 0:
                Exif['GPS IFD'][GPSTAGS[6]] = '%fm above sea level' % Exif['GPS IFD'][GPSTAGS[6]]
            elif GPSAltitudeRef == 1:
                Exif['GPS IFD'][GPSTAGS[6]] = '%fm below sea level' % Exif['GPS IFD'][GPSTAGS[6]]
        if GPSTAGS[7] in Exif['GPS IFD']:# GPSTimeStamp
            Exif['GPS IFD'][GPSTAGS[7]] = '%d:%d:%.2f' % Exif['GPS IFD'][GPSTAGS[7]]
        if GPSTAGS[12] in Exif['GPS IFD']:# GPSSpeedRef
            unit = {'K': ' km/h', 'M': ' mph', 'N': ' knots'}[Exif['GPS IFD'].pop(GPSTAGS[12])]
            Exif['GPS IFD'][GPSTAGS[13]] = str(Exif['GPS IFD'][GPSTAGS[13]]) + unit
        if GPSTAGS[14] in Exif['GPS IFD']:# GPSTrackRef
            GPSTrackRef = {
                'T': 'ﾟ (true direction)', 'M': 'ﾟ (magnetic direction)'
            }[Exif['GPS IFD'].pop(GPSTAGS[14])]
            Exif['GPS IFD'][GPSTAGS[15]] = str(Exif['GPS IFD'][GPSTAGS[15]]) + GPSTrackRef
        if GPSTAGS[16] in Exif['GPS IFD']:# GPSImgDirectionRef
            GPSImgDirectionRef = {
                'T': 'ﾟ (true direction)', 'M': 'ﾟ (magnetic direction)'
            }[Exif['GPS IFD'].pop(GPSTAGS[16])]
            Exif['GPS IFD'][GPSTAGS[17]] = str(Exif['GPS IFD'][GPSTAGS[17]]) + GPSImgDirectionRef
        if GPSTAGS[19] in Exif['GPS IFD']:# GPSDestLatitudeRef
            dd, mm, ss = Exif['GPS IFD'][GPSTAGS[20]]
            dd = str(int(dd))
            if mm == int(mm):
                mm, ss = str(int(mm)), str(ss)
            else:
                mm, ss = str(mm), ''
            Exif['GPS IFD'][GPSTAGS[20]] = '%sﾟ %s\' %s" %s' % (dd, mm, ss, Exif['GPS IFD'].pop(GPSTAGS[19]))
        if GPSTAGS[21] in Exif['GPS IFD']:# GPSDestLongitudeRef
            dd, mm, ss = Exif['GPS IFD'][GPSTAGS[22]]
            dd = str(int(dd))
            if mm == int(mm):
                mm, ss = str(int(mm)), str(ss)
            else:
                mm, ss = str(mm), ''
            Exif['GPS IFD'][GPSTAGS[22]] = '%sﾟ %s\' %s" %s' % (dd, mm, ss, Exif['GPS IFD'].pop(GPSTAGS[21]))
        if GPSTAGS[23] in Exif['GPS IFD']:# GPSDestBearingRef
            GPSDestBearingRef = {
                'T': 'ﾟ (true direction)', 'M': 'ﾟ (magnetic direction)'
            }[Exif['GPS IFD'].pop(GPSTAGS[23])]
            Exif['GPS IFD'][GPSTAGS[24]] = str(Exif['GPS IFD'][GPSTAGS[24]]) + GPSDestBearingRef
        if GPSTAGS[25] in Exif['GPS IFD']:# GPSDestDistanceRef
            unit = {'K': ' km', 'M': ' mi', 'N': ' nmi'}[Exif['GPS IFD'].pop(GPSTAGS[25])]
            Exif['GPS IFD'][GPSTAGS[26]] = str(Exif['GPS IFD'][GPSTAGS[26]]) + unit
        if GPSTAGS[31] in Exif['GPS IFD']:# GPSHPositioningError
            Exif['GPS IFD'][GPSTAGS[31]] = str(Exif['GPS IFD'][GPSTAGS[31]]) + 'm'
    return Exif