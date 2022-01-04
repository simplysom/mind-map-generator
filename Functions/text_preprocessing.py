import re
from . import global_variables as gv
from .logging import log, log_return

gv.PREPROCESSING_PIPELINE={
    "article-numbers":{
        "description":"removing article reference numbers",
        "parameters":("[^s]*\[[a-zA-Z0-9._%+-]*\]",""), #("\[[0-9]*]",""),
        "function":re.sub
    },
    "percentage-values":{
        "description":"removing all percentage values",
        "parameters":(" \d+(?:.\d*)?\%",""),
        "function":re.sub
    },
    "numbers":{
        "description":"removing all numbers",
        "parameters":("[\d+,]*\d+",""),
        "function":re.sub
    },
    "non-english-characters":{
        "description":"removing all non english characters",
        "parameters":("[^\u0000-\u007F]+",""),
        "function":re.sub
    },
	"new-line":{
        "description":"REplacing multiple new line characters with single newline characters",
        "parameters":("\\n+", "\\n"),
        "function":re.sub
	},
}

@log_return
def preprocess(text,preprocessing_pipeline):
    result=text
    for a,b in preprocessing_pipeline.items():
        result=b["function"](*b["parameters"],result)
    return result
