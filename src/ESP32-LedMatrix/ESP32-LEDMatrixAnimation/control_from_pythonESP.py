import urllib2
import time;
import os;
from math import *
import random;
import pdb

# taken from :
# https://xantorohara.github.io/led-matrix-editor/#0010107c10100000|0000003c00000000|006c38fe386c0000|00060c1830600000|60660c1830660600|00003c003c000000|000000365c000000|0000008244281000|6030180c18306000|060c1830180c0600|6030181818306000|060c1818180c0600|7818181818187800|1e18181818181e00|7018180c18187000|0e18183018180e00|0606000000000000|0018180018180000|0c18180018180000|060c0c0c00000000|180018183c3c1800|1800183860663c00|003c421a3a221c00|fc66a6143c663c00|103c403804781000|6c6cfe6cfe6c6c00|383838fe7c381000|10387cfe38383800|10307efe7e301000|1018fcfefc181000|fefe7c7c38381000|1038387c7cfefe00|061e7efe7e1e0600|c0f0fcfefcf0c000|7c92aa82aa827c00|7ceed6fed6fe7c00|10387cfefeee4400|10387cfe7c381000|381054fe54381000|38107cfe7c381000|00387c7c7c380000|ffc7838383c7ffff|0038444444380000|ffc7bbbbbbc7ffff|0c12129ca0c0f000|38444438107c1000|060e0c0808281800|066eecc88898f000|105438ee38541000|1038541054381000|6666006666666600|002844fe44280000|00000000286c6c00|006030180c060000|0000000060303000|0000000c18181800|fe8282c66c381000
charList = [
      0x6666667e66663c00,
      0x3e66663e66663e00,
      0x3c66060606663c00,
      0x3e66666666663e00,
      0x7e06063e06067e00,
      0x0606063e06067e00,
      0x3c66760606663c00,
      0x6666667e66666600,
      0x3c18181818183c00,
      0x1c36363030307800,
      0x66361e0e1e366600,
      0x7e06060606060600,
      0xc6c6c6d6feeec600,
      0xc6c6e6f6decec600,
      0x3c66666666663c00,
      0x06063e6666663e00,
      0x603c766666663c00,
      0x66361e3e66663e00,
      0x3c66603c06663c00,
      0x18181818185a7e00,
      0x7c66666666666600,
      0x183c666666666600,
      0xc6eefed6c6c6c600,
      0xc6c66c386cc6c600,
      0x1818183c66666600,
      0x7e060c1830607e00,
      0x0000000000000000,
      0x7c667c603c000000,
      0x3e66663e06060600,
      0x3c6606663c000000,
      0x7c66667c60606000,
      0x3c067e663c000000,
      0x0c0c3e0c0c6c3800,
      0x3c607c66667c0000,
      0x6666663e06060600,
      0x3c18181800180000,
      0x1c36363030003000,
      0x66361e3666060600,
      0x1818181818181800,
      0xd6d6feeec6000000,
      0x6666667e3e000000,
      0x3c6666663c000000,
      0x06063e66663e0000,
      0xf0b03c36363c0000,
      0x060666663e000000,
      0x3e403c027c000000,
      0x1818187e18180000,
      0x7c66666666000000,
      0x183c666600000000,
      0x7cd6d6d6c6000000,
      0x663c183c66000000,
      0x3c607c6666000000,
      0x3c0c18303c000000];

letterList = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz';

digitList = [  0x7e1818181c181800,
               0x7e060c3060663c00,
               0x3c66603860663c00,
               0x30307e3234383000,
               0x3c6660603e067e00,
               0x3c66663e06663c00,
               0x1818183030667e00,
               0x3c66663c66663c00,
               0x3c66607c66663c00,
               0x3c66666e76663c00]

# Row first ordering of data:




def writeRaw(rawDat):

    req = urllib2.Request("http://192.168.0.100/ImgData",rawDat);
    req.get_method = lambda: 'PUT';
    urllib2.urlopen(req);

def intMatrixToBytes(r,g,b):

    r_tot = bytearray([]);
    g_tot = bytearray([]);
    b_tot = bytearray([]);

    for k in range(0,10):
        direction  = k%2
        if direction == 0:
            r_raw = [aa for aa in bytearray(r[k][:])];
            g_raw = [bb for bb in bytearray(g[k][:])];
            b_raw = [cc for cc in bytearray(b[k][:])];
        else:
            r_raw = [aa for aa in reversed(bytearray(r[k][:]))];
            g_raw = [bb for bb in reversed(bytearray(g[k][:]))];
            b_raw = [cc for cc in reversed(bytearray(b[k][:]))];

        r_tot = r_tot + bytearray(r_raw);
        g_tot = g_tot + bytearray(g_raw);
        b_tot = b_tot + bytearray(b_raw);

    tot_data = bytearray([k for k in 'START_IMG_DATA'] ) + r_tot + g_tot  + b_tot

    return tot_data;

def hexCharToMatrix(charRep,v,o1=0,o2=0,transpose=False):
    cc = str(bin(charRep));
    cc = cc[2:];
    cc = ((64 - len(cc)) * "0") + cc;

    mm = [[0 for i in range(0,15)] for k in range(0,10)];
    pp = 0;
    for k in range(0,8):
        for m in range(0,8):
            mm[m+o1][k+o2] = int(cc[pp]) * v;
            pp = pp +1;

    return mm;

def flipY(m):
    mm = [[zz for zz in reversed(k)] for k in reversed(m)]
    return mm

def animChars():
    word = 'ASDF';

    M0 = [[0 for i in range(0,15)] for j in range(0,10)];
    M = intMatrixToBytes(M0,M0,M0);
    writeRaw(M);

    for i in word:
        idx = letterList.find(i);
        mr  = hexCharToMatrix(charList[idx],random.randint(10,150),1,1);
        mg  = hexCharToMatrix(charList[idx],random.randint(10,150),1,1);
        mb  = hexCharToMatrix(charList[idx],random.randint(10,150));
        mr = flipY(mr)
        mg = flipY(mg)
        mb = flipY(mb)


        #mr = hexCharToMatrix(charList[idx],150,1,1);
        #mg = hexCharToMatrix(charList[idx],150,1,1);
        #mb = hexCharToMatrix(charList[idx],150,1,1);

        M = intMatrixToBytes(mr,mg,mb);

        writeRaw(M);
        time.sleep(1);

def slideWord(word,delay, repeat = 1):

    Mr = [];
    Mb = [];
    Mg = [];

    for i in word:
        idx = letterList.find(i);
        mr  = hexCharToMatrix(charList[idx],random.randint(10,250),-7,-8);
        mg  = hexCharToMatrix(charList[idx],random.randint(10,250),-7,-8);
        mb  = hexCharToMatrix(charList[idx],random.randint(10,250),-7,-8);
        mr = flipY(mr)
        mg = flipY(mg)
        mb = flipY(mb)


        Mr = Mr + mr;
        Mg = Mg + mg;#[Mg + mm for mm in mg];
        Mb = Mb + mb;#[Mb + mm for mm in mb];

        #mr = hexCharToMatrix(charList[idx],150,1,1);
        #mg = hexCharToMatrix(charList[idx],150,1,1);
        #mb = hexCharToMatrix(charList[idx],150,1,1);

    for mm in range(0, repeat):
        # Slide the word:
        for kk in range(0, len(Mr)-10):
            mr = Mr[kk:kk+10];
            mg = Mg[kk:kk+10];
            mb = Mb[kk:kk+10];
            M = intMatrixToBytes(mr,mg,mb);
            writeRaw(M);
            time.sleep(delay);

def slideAsciiArt(asciifile = 'mario.ascii', delay = 0.01, repeat = 20):
    f = open(asciifile,'r');
    z = f.read();
    dds = z.split('\n');
    # For smiley:
    if asciifile == 'smiley.ascii':
        char2col = {' ':[10, 0, 10], 'x':[0, 0, 0], '.':[235, 235, 10],'o':[10, 10, 10],
                '-' : [0, 0, 0], '\\': [0, 0, 0],'|':[0, 0, 0], '/':[0,0,0] , ('_' , ':', '(', ')' ,'`','\'',',') : [0 , 0, 0]};
    if asciifile == 'mario.ascii':
        char2col = {' ':[5, 5, 5],
                    'h':[0, 0, 80] ,
                    'r':[90, 0, 0],
                    'y':[50,50,40],
                    'v' :[109, 79, 29] ,
                    'b':[102,21,0]};

    if asciifile == 'donought.ascii':
        char2col = {' ':[0, 10 , 10] , 'r':[50, 0 , 0] , 'b':[0 , 0 , 50],
                    'p':[150,110,0],
                    '0':[0,0,0],
                    'w':[109,79,29],
                    'y':[50,50,40],
                    'g':[0,100,0]};

    # Background can also be a function
    Mr =  [[char2col[n][0] for n in k] for k in dds[:-1]];
    Mg =  [[char2col[n][1] for n in k] for k in dds[:-1]];
    Mb =  [[char2col[n][2] for n in k] for k in dds[:-1]];

    Mr = map(list, zip(*Mr))
    Mb = map(list, zip(*Mb))
    Mg = map(list, zip(*Mg))



    tt=0.1;
    for mm in range(0, repeat):
        for kk in range(0, len(Mr)-10):
            tt=tt-0.005;
            mr = Mr[kk:kk+10][0:15];
            mg = Mg[kk:kk+10][0:15];
            mb = Mb[kk:kk+10][0:15];
            for i in range(0,10):
                for j in range(0, 15):
                    if mr[i][j] == -1:
                        rr = 60;
                        fr = min(max(rr*2+cos(float(i)/10/2*2*pi+tt)*rr+ sin(float(j)/15/2*2*pi+tt)*rr,0),200)
                        mr[i][j] = int(round(fr));
                    if mb[i][j] == -1:
                        rg = 50
                        fb = min(max(rg*2+cos(float(i)/10*2*pi+pi/3+tt)*rg + sin(float(j)/15*2*pi+pi/3+2*tt)*rg,0),200)
                        mb[i][j] = int(round(fb));
                    if mg[i][j] == -1:
                        mg[i][j] = 0*int(round(20+sin(i*pi/10*tt*2)*10));

            #pdb.set_trace()
            M = intMatrixToBytes(mr,mg,mb);
            writeRaw(M);
            time.sleep(delay);




def anim0(reps=0):
    t=0

    rr = random.randint(25,100);
    rg = random.randint(25,100);
    for i in range(1,reps):
        t = t+0.1;
        M = [[0 for i in range(0,15)] for j in range(0,10)];
        Mr = [[0 for i in range(0,15)] for j in range(0,10)];
        Mg = [[0 for i in range(0,15)] for j in range(0,10)];
        Mb = [[0 for i in range(0,15)] for j in range(0,10)];
        M0 = [[0 for i in range(0,15)] for j in range(0,10)];

        for k in range(0,15):
            for m in range(0,10):

                fr = min(max(rr*2+cos(float(m)/10/2*2*pi+t)*rr+ sin(float(k)/15/2*2*pi+t)*rr,0),200)

                fb = min(max(rg*2+cos(float(m)/10*2*pi+pi/3+t)*rg + sin(float(k)/15*2*pi+pi/3+2*t)*rg,0),200)

                fg =0; random.randint(25,60)+cos(float(m)/10*2*pi+pi/3+t)*50 + sin(float(k)/15*2*pi+pi/3+2*t)*25
                Mr[m][k] = int(round(fr));
                Mg[m][k] = int(round(fg));
                Mb[m][k] = int(round(fb));


        rmat = intMatrixToBytes(Mr,Mg,Mb);
        writeRaw(rmat);



def anim1():
    while(True):
        for k in range(0,15):
            for m in range(0,10):
                M = [[0 for i in range(0,15)] for j in range(0,10)];
                M0 = [[0 for i in range(0,15)] for j in range(0,10)];
                M[m][k] = max(250-m*25,0);
                time.sleep(0.01);
                rmat = intMatrixToBytes(M0,M,M);

                writeRaw(rmat);



def anim2():
    # a loop:
    while(True):
        # Loops the red channel and keeps the rest constant:
        imdat_old = bytearray(os.urandom(450));
        for kk in range(10,150,20)+[i for i in reversed(range(10,150,20))] :
            #data=bytearray([a for a in 'START_IMG_DATA'] + [0 for i in range(0,150)]+[kk for i in range(0, 150)] + [120 for i in range(0,150)]);
            imdat_new = bytearray([kk for i in range(0,150)]);
            imdat_new = imdat_new + bytearray([0 for i in range(0,150)]);
            imdat_new = imdat_new + bytearray([0 for i in range(0,150)]);

            data=bytearray([a for a in 'START_IMG_DATA']) + imdat_new;
            writeRaw(data)
            time.sleep(0.01);

            #data=bytearray([a for a in 'START_IMG_DATA'] + [0 for i in range(0,150)]+[0 for i in range(0, 150)] + [0 for i in range(0,150)]);
            #req = urllib2.Request("http://192.168.0.100/ImgData",data);
            #req.get_method = lambda: 'PUT';
            #urllib2.urlopen(req);

            time.sleep(0.001);

if __name__ == '__main__':


    while(True):



        slideAsciiArt(asciifile='donought.ascii',delay=0.2,repeat = 2)
        slideAsciiArt(asciifile='mario.ascii',repeat = 1)
        slideWord('Hello world',0.01, repeat = 1)
        anim0(reps = 40)
        slideAsciiArt(asciifile='mario.ascii',repeat = 1)
        slideAsciiArt(asciifile='smiley.ascii',repeat = 1)

