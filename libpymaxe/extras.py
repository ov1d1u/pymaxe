# Extra functions for Pymaxe library
# The code in this file are property of their owners

def delete_module(modname, paranoid=None):					# (c) Michael P. Reilly
    from sys import modules
    try:
        thismod = modules[modname]
    except KeyError:
        raise ValueError(modname)
    these_symbols = dir(thismod)
    if paranoid:
        try:
            paranoid[:]  # sequence support
        except:
            raise ValueError('must supply a finite list for paranoid')
        else:
            these_symbols = paranoid[:]
    del modules[modname]
    for mod in modules.values():
        try:
            delattr(mod, modname)
        except AttributeError:
            pass
        if paranoid:
            for symbol in these_symbols:
                if symbol[:2] == '__':  # ignore special symbols
                    continue
                try:
                    delattr(mod, symbol)
                except AttributeError:
                    pass
	    
def output_exc(level=3):
	import sys, traceback
	error_type, error_value, trbk = sys.exc_info()
	tb_list = traceback.format_tb(trbk, level)    
	info_list = ["Error: %s \nDescription: %s \nTraceback:\n" % (error_type.__name__, error_value), ]
	info_list.extend(tb_list)
	print ''.join(info_list)