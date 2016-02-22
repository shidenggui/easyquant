# coding: utf-8
import talib
import numpy

def high( nd , iWindow ):
    return (talib.MAX( nd , iWindow ), talib.MAXINDEX(nd, iWindow) );

def low( nd, iWindow ):
    return (talib.MIN( nd, iWindow ) , talib.MININDEX( nd, iWindow ) );

def uphigh(nd,iWindow):
    prehigh = talib.MAX( nd[:-1] ,iWindow );
    if( nd[-1] > prehigh[-1]):
        return  True
    else:
        return False;

def downlow(nd,iWindow):
    prelow = talib.MIN( nd[:-1] ,iWindow );
    if( nd[-1] < prelow[-1]):
        return  True
    else:
        return False;

if __name__ == '__main__':
    arr = numpy.array([ 8.,  8.,  3.,  9.,  8.,  4.,  3.,  2.,  2.,  6.,  4.,  1.]);
    uphigh( arr , 5 );
    downlow( arr, 5);
    pass
