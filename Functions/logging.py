from collections import defaultdict
from functools import wraps
import sys
from . import global_variables as gv
from timeit import default_timer as timer

def log(fn):
	"""Logs function name, function arguments and number of time the function was called in LOG variables"""
	@wraps(fn)
	def inside(*args, **kwargs):
		gv.FUNCTION_COUNT[fn.__name__] += 1
		gv.LOG_FILE += f'fn : {fn.__name__} | args : {args, kwargs}\n'
		return fn(*args, **kwargs)
	return inside


def log_return(fn):
	"""Logs return value for a function along with function name in LOG variables"""
	@wraps(fn)
	def inside(*args, **kwargs):
		return_value = fn(*args, **kwargs)
		gv.RETURN_LOG_FILE += f'Fn : {fn.__name__}\n{return_value}\n\n'
		return return_value
	return inside  


def timefn(fn):
    """Times a function and stores the result in LOG variables"""
    @wraps(fn)
    def inside(*args, **kwargs):
        start = timer()
        result = fn(*args, **kwargs)
        end = timer()
        gv.TIME_LOG += f'Fn : {fn.__name__} - {end - start}\n'
        return result
    return inside 


# Stat function.
def print_count_pairs(a):
    count = 0
    for n1,n2 in a:
        n1_sent_inst={n.sent for n in n1._.instance_list}
        n2_sent_inst={n.sent for n in n2._.instance_list}
        common_sent=n1_sent_inst.intersection(n2_sent_inst)
        if common_sent:
            # print("\t\t", n1,n2)
            count+=1
    print("In-Sentence Pair Ratio\t\t   :",count/len(a))

