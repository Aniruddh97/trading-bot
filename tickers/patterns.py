import talib

def getCandlePatternList(all=False):
    if not all:
        return ['CDLDARKCLOUDCOVER', 'CDLDOJI', 'CDLENGULFING', 'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR', 'CDLHAMMER', 'CDLHANGINGMAN', 'CDLHARAMI', 'CDLMARUBOZU', 'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR', 'CDLPIERCING', 'CDLSHOOTINGSTAR', 'CDLSPINNINGTOP']
    return talib.get_function_groups()['Pattern Recognition']
