DELIM = '/'

def make_symbol(*args):
    """
    Returns a canonical symbol for an arbitrary set of parameters.
    Result is independent of argument ordering.
    
    example: make_symbol('BTC', 'USD') => 'BTC/USD'
             make_symbol('USD', 'BTC') => 'BTC/USD'
    
    """
    
    return DELIM.join(sorted(map(str, args)))
