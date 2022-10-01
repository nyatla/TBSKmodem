from typing import Sequence, overload
import math

def points2Liner(x:Sequence[float],y:Sequence[float]):
    """ 最小二乗法で近似直線の係数を計算します。
    
    @Returns
        ax+by+c=0の係数a,b,cを返します。

    """
    assert(len(x)==len(y))
    number_of_data=len(x)
    sum_xy = 0
    sum_x = 0
    sum_y = 0
    sum_x2 = 0
    for i in range(number_of_data):
        # NyARDoublePoint2d ptr=i_points[i];
        xw=x[i]
        sum_xy += xw * y[i]
        sum_x += xw
        sum_y += y[i]
        sum_x2 += xw*xw
    b =-(number_of_data * sum_x2 - sum_x*sum_x)
    a = (number_of_data * sum_xy - sum_x * sum_y)
    c = (sum_x2 * sum_y - sum_xy * sum_x)
    return a,b,c


def npi(v):
    """ [-π,π]に正規化する
    """
    pi2=math.pi*2
    #[-2pi,2pi]にする。
    v=v%pi2
    #[0,2pi]反時計回りにする。
    if v<0:
        v=pi2+v
    #[-π,π]にする。
    return v if v<=math.pi else v-2*math.pi


def bitCount(bits:int):
    assert(bits<=0xffffffff and bits>=0)
    bits = (bits & 0x55555555) + (bits >> 1 & 0x55555555)
    bits = (bits & 0x33333333) + (bits >> 2 & 0x33333333)
    bits = (bits & 0x0f0f0f0f) + (bits >> 4 & 0x0f0f0f0f)
    bits = (bits & 0x00ff00ff) + (bits >> 8 & 0x00ff00ff)
    return (bits & 0x0000ffff) + (bits >>16 & 0x0000ffff)

import struct
from typing import Union

BITSEQUENCEABLE=Union[bytes,str]

def hummingDistance(a:BITSEQUENCEABLE,b:BITSEQUENCEABLE):
    """ ビット列aとbのハミング距離を返します。
    """
    if isinstance(a,str):
        a=a.encode("utf-8")
    if isinstance(b,str):
        b=b.encode("utf-8")

    assert(len(a)==len(b))
    l=len(a)
    r=0
    m=l%4
    n=l-m
    for i in range(0,n,4):
        ai=struct.unpack("<L",a[i:i+4])
        bi=struct.unpack("<L",b[i:i+4])
        r=r+bitCount(ai[0] ^ bi[0])
        # print(i,bitCount(ai[0] ^ bi[0]),str(bin(ai[0] ^ bi[0])))
    for i in range(l-m,l):
        # ai=struct.unpack("<B",a[i])
        # bi=struct.unpack("<B",b[i])
        r=r+bitCount(a[i] ^ b[i])
    return r
