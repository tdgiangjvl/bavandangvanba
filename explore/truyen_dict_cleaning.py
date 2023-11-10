from data_utils import *
import pandas as pd
init_logger()
n_gram_phrases = pd.read_pickle(os.path.join(PRJ_BASE,'tmp/dictionary_from_truyen_data_raw.pkl'))
n_gram_phrases = clean_upper_case(n_gram_phrases)
logging.info('  - Cleaned upper case')
pd.to_pickle(n_gram_phrases, os.path.join(PRJ_BASE,'tmp/dictionary_from_truyen_data.pkl'))