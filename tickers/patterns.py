import talib

def getCandlePatternList(all=False):
    if not all:
        return ['CDLENGULFING', 'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR', 'CDLHAMMER', 'CDLHANGINGMAN', 'CDLHARAMI', 'CDLMARUBOZU', 'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR', 'CDLSHOOTINGSTAR']
    return talib.get_function_groups()['Pattern Recognition']
