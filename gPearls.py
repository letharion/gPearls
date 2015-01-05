#!/usr/bin/python

import sys, getopt
import Image, ImageDraw

class ColorRegister:
    index = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

# These are the pearl color used by the original PhotoPearls software
colors = [
    (0x17, 0x20, 0x29),(0x48, 0x3f, 0x38),
    (0x57, 0x3b, 0x38),(0x80, 0x1f, 0x32),
    (0xb3, 0x61, 0x2f),(0xa9, 0x90, 0x7c),
    (0xe4, 0xb1, 0x84),(0x9b, 0x9b, 0x93),
    (0x33, 0x4c, 0x39),(0xda, 0xd1, 0xd4),
    (0x61, 0x44, 0x98),(0xe0, 0xd5, 0xc3),
    (0xe5, 0x4e, 0x31),(0xe4, 0xc3, 0x42),
    (0xf6, 0xf6, 0xf4),(0x26, 0x76, 0x37),
    (0x3d, 0x75, 0xd2),(0xdc, 0xac, 0xa8),
    (0xca, 0x2a, 0x2a),(0xb7, 0x77, 0x53),
    (0xf5, 0xe3, 0x81),(0x3c, 0x99, 0x3e),
    (0x65, 0x9d, 0xe8),(0xb6, 0xa7, 0xe2),
    (0xf4, 0x6b, 0x97),(0xff, 0x9f, 0x6d),
    (0x78, 0x45, 0x34),(0x9e, 0xc3, 0xed),
    (0xee, 0x82, 0x27),(0xb4, 0xad, 0x3b),
]


def getMeanColor(data, size, x0, y0, w, h):
    """
    Returns the mean color of the pixels in the definex square
    """
    rgb = [0,0,0]
    for y in range(h):
        index = x0 + (y0+y)*size[0]
        for x in range(w):
            value = data[index]

            rgb[0] += value[0]
            rgb[1] += value[1]
            rgb[2] += value[2]

            index += 1

    isize = 1.0/(w*h)
    rgb[0] *= isize
    rgb[1] *= isize
    rgb[2] *= isize

    return rgb

def findMatchingColor(color):
    """
    Find the closest matching color, and return its index.
    """
    closest = 0
    closestDist = 255*255*3

    for i in range(len(colors)):
        c = colors[i]
        dist = (c[0]-color[0])*(c[0]-color[0]) + (c[1]-color[1])*(c[1]-color[1]) + (c[2]-color[2])*(c[2]-color[2])

        if dist < closestDist:
            closestDist = dist
            closest = i

    return closest


def generate(im, size, offset, dest, colorCount, mirror):
    width = size[0]
    height = size[1]
    pw = im.size[0] / width
    ph = im.size[1] / height

    if ph < pw:
        pw = ph
    if pw < ph:
        ph = pw

    print "Using the area %s->%s" % (str(offset), str((offset[0]+width*pw, offset[1]+height*ph)))

    tw = 22
    th = 22

    target = Image.new("RGB", (width*tw, height*th))
    draw = ImageDraw.Draw(target)
    data = im.getdata()
            
    print "Generating image..."
    if colorCount != "":
        colorIndex = ColorRegister()

    for y in range(height):
        for x in range(width):
            mean = getMeanColor(data, im.size, x*pw, y*ph, pw, ph)
            index = findMatchingColor(mean)
            color = colors[index]

            if colorCount != "":
              colorIndex.index[index] += 1

            if (mirror):
                 draw.rectangle([( (width - x) * tw, y*th), ((width - x - 1) * tw, (y+1)*th)], fill=color)
            else:
                 draw.rectangle([(x*tw, y*th), ((x+1)*tw, (y+1)*th)], fill=color)

            size = draw.textsize(str(index+1))
            
            ox = (pw-size[0]) / 2
            oy = (ph-size[1]) / 2

            if (mirror):
                text_x = (width - x - 1) * tw + ox + 2 + (size[0] / 2)
            else:
                text_x = x * tw + ox + (size[0] / 2)

            text_y = y * th + oy + (size[1] / 2)
            draw.text((text_x, text_y - 1), str(index+1), fill=0x000000)
            draw.text((text_x, text_y + 1), str(index+1), fill=0x000000)
            draw.text((text_x - 1, text_y), str(index+1), fill=0x000000)
            draw.text((text_x + 1, text_y), str(index+1), fill=0x000000)
            draw.text((text_x, text_y), str(index+1), fill=0xffffff)
    del draw

    print colorCount
    if colorCount != "":
        f = open(colorCount, 'a')
        f.write("\t".join(str(x) for x in colorIndex.index) + "\n")


    if dest:
        target.save(dest, "JPEG")
    target.show()


def help():
    print "gPearl 1.0, 2009, http://static.slackers.se/pages/gpearls/"
    print ""
    print "Usage gPearl [-s size] [-o offset] [-d dest] <IMAGE>"
    print ""
    print "  -h, --help       This help screen."
    print "  -s, --size       The size of the pearlplate (default is 30x30)."
    print "  -d, --dest       The location of the output file."
    print "  -o, --offset     The offset to use of the original image (deafult is 0x0)."
    print "  -c, --colorcount The location of the colorcount output file. Data is always appended."
    print ""
    sys.exit(0)


def parse(v):
    part = v.split('x')
    if len(part) != 2:
        print "Error: Invalid format '%s'. Expected '<NUMBER>x<NUMBER>'" % v
        sys.exit(-1)
    try:
        return (int(part[0]), int(part[1]))
    except ValueError:
        print "Error: Invalid format '%s'. Expected '<NUMBER>x<NUMBER>'" % v
        sys.exit(-1)

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'mhs:o:d:c:', ['help', 'size=', 'offset=', 'dest=', 'colorcount=', 'mirror'])

    if len(args) != 1:
        help()

# Default values
    image = args[0]
    size = (30, 30)
    offset = (0, 0)
    dest = None
    colorCount = ""
    mirror = False

    for k,v in optlist:
        if k in ('-h', '--help'):
            help()
        if k in ('-s', '--size'):
            size = parse(v)
        if k in ('-o', '--offset'):
            offset = parse(v)
        if k in ('-d', '--dest'):
            dest = v
        if k in ('-c', '--colorcount'):
            colorCount = v
        if k in ('-m', '--mirror'):
            mirror = True

    print "Using image: " + image
    print "  Size: " + str(size)
    print "  Offset: " + str(offset)
    if dest:
        print "  Destination file: " + dest


    im = Image.open(image)
    generate(im, size, offset, dest, colorCount, mirror)
except Exception, e:
    print "Error: ", e
    help()
