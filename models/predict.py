"""
Predicts job satisfaction based on models trained by the Stack Overflow Developer Survey.
"""
import os
import xgboost as xgb

FEATS_2015 = [
    ('Compensation: midpoint', 'salary'),
    ('Purchasing Power_I have no say in purchasing what I need or want at work',
     'no_purchase_power'),
    ('Remote Status_Never', 'remote'),
    ('Changed Jobs in last 12 Months', 'curr_job_less_than_year'),
]

FEATS_2016 = [
    ('agree_loveboss', 'like_boss'),
    ('agree_tech', 'job_technologies'),
    ('open_to_new_job_I am actively looking for a new job', 'look_postings_frequent'),
    ('interview_likelihood', 'interview'),
]

FEATS_2017 = [
    ('CareerSatisfaction', 'like_developer'),
    ('HoursPerWeek', 'hours_per_week'),
    ('Overpaid', 'overpaid'),
    ('LastNewJob_Less than a year ago', 'curr_job_less_than_year'),
    ('InfluenceWorkstation', 'choose_equip'),
    ('Salary', 'salary'),
]

CURR_FOLDER = os.path.dirname(os.path.realpath(__file__))
XGB_2015 = xgb.Booster(model_file=os.path.join(CURR_FOLDER, 'output2015.model'))
XGB_2016 = xgb.Booster(model_file=os.path.join(CURR_FOLDER, 'output2016.model'))
XGB_2017 = xgb.Booster(model_file=os.path.join(CURR_FOLDER, 'output2017.model'))

MODELS = (
    [XGB_2015, FEATS_2015],
    [XGB_2016, FEATS_2016],
    [XGB_2017, FEATS_2017],
)

NUM_MODELS = len(MODELS)
REQUIRED_KEYS = set(feat[1] for model in MODELS for feat in model[1])

TRAIN_OPTIONS = {
    'silent': True,
}

def clip(num, low, high):
    """
    Replicates np.clip.
    """
    if num < low:
        return low

    if num > high:
        return high

    return num

def preproc(user_in):
    """
    Add extra values necessary for the models to run.
    """
    user_in['look_postings_frequent'] = float(user_in['hours_per_week'] > 1)
    user_in['no_purchase_power'] = float(float(user_in['choose_equip']) == 1.0)
    user_in['remote'] = 1.0 - float(user_in['remote'])

    return {key: float(user_in[key]) for key in REQUIRED_KEYS}

def get_year_dmatrix(user_in, year, label=None):
    """
    Get the xgb.DMatrix to input into the xgboost Booster functions.
    """
    feats = [feat[0] for feat in MODELS[year][1]]
    model_in = [float(user_in[feat[1]]) for feat in MODELS[year][1]]

    return xgb.DMatrix(model_in, feature_names=feats, label=label)

def predict(user_in):
    """
    Predict job satisfaction using the data provided.
    If user_in does not contain all REQUIRED_KEYS, returns -1.
    """
    try:
        to_predict = preproc(user_in)
    except (ValueError, TypeError, KeyError):
        return -1

    out = sum(MODELS[year][0].copy().predict(get_year_dmatrix(to_predict, year))[0]
              for year in xrange(NUM_MODELS)) / NUM_MODELS
    return clip(out, 0, 10)

def train(user_in, job_satisfaction):
    """
    Incremental training: add the most recent observation to the model.
    """
    global MODELS

    try:
        to_train = preproc(user_in)
        job_satisfaction = float(job_satisfaction)
    except (ValueError, TypeError, KeyError):
        return False

    for year in xrange(NUM_MODELS):
        new_x = get_year_dmatrix(to_train, year, [job_satisfaction])
        MODELS[year][0] = xgb.train(TRAIN_OPTIONS, new_x, xgb_model=MODELS[year][0].copy())

    return True
