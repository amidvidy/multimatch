DELIM = '/'

def make_symbol(*args):
    """Returns a canonical symbol for an arbitrary set of parameters
    e.g. make_symbol('BTC', 'USD') => 'BTC/USD'"""
    
    return DELIM.join(sorted(map(str, args)))