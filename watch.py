import json
import datetime
import xml.etree.ElementTree as ET

import boto3
import pandas as pd

hit_id = '3LG268AV38EKMT05IFZVI59WEFTER9'
qualification_id = '3090SA10WLFCWLA7KTT2V8PINSECNG'
limit = 85


email_pass = '''Dear {worker},
We are pleased to inform you that you pass the qualification test from the HIT "{project}". Your score is {score} out of 105, which exceeds the minimal requirement of the qualification (at least 80% correctness). You will receive $4.5 for completing and passing the qualification HIT.

We look forward to working with you. Please proceed to work on the HITs "{project}".
'''

email_fail = '''Dear {worker},
We regret to inform you that you did not pass the qualification test from the HIT "{project}". Your score is {score} out of 105, which did not exceed the minimal requirement of the qualification (at least 80% correctness). 
To work on the HITs "{project}", you will need to pass the qualification test. You can re-take the qualification HIT "{project_test}"" after 24 hours.
'''

client = boto3.client('mturk',
                      region_name='us-east-1',
                      endpoint_url='https://mturk-requester-sandbox.us-east-1.amazonaws.com')

def calc_ans():
    df = pd.read_csv('training tweet sets - 25 for gun issues.csv')
    df = df.fillna('')
    ex = pd.read_csv('export2.csv', index_col='TweetID')
    text_clean = ex.loc[df['id'].tolist()]['text_clean'].tolist()

    def ans(s):
        if not s:
            return ''
        else:
            return s.lower().split()[0]

    res = []
    for i, row in df.iterrows():
        res.append([row['id'], text_clean[i], ans(row['q1']), ans(row['q3'])])

    ans1 = [j for _, i, j, k in res]
    ans3 = [k for _, i, j, k in res]

    return ans1, ans3

ans1, ans3 = calc_ans()

survey_head = ['Age.30-39', 'Age.40-49', 'Age.50-59', 'Age.60+', 'Age.Prefer not to say', 'Age.Under 30',
                "Education.Bachelor's degree", 'Education.College degree', 'Education.Doctorate degree',
                'Education.High school diploma', 'Education.Less than high school degree', "Education.Master's degree",
                'Education.Other (please specify)', 'Education.Prefer not to say', 'Gender.Female', 'Gender.Male',
                'Gender.Non-binary', 'Gender.Prefer not to say', 'Ideological preferences.Conservative',
                'Ideological preferences.Liberal', 'Ideological preferences.Moderate', 'Ideological preferences.Other (please specify)',
                'Ideological preferences.Prefer not to say', 'Ideological preferences.Unsure',
                'Location.East North Central - Illinois,Indiana, Michigan, Ohio, Wisconsin',
                'Location.East South Central - Alabama, Kentucky, Mississippi, Tennessee',
                'Location.Middle Atlantic - New Jersey, New York, Pennsylvania',
                'Location.Mountain - Arizona, Colorado, Idaho, Montana, Nevada, New Mexico, Utah, Wyoming',
                'Location.New England - Connecticut, Maine, Massachusetts, New Hampshire, Rhode Island, Vermont',
                'Location.Pacific - Alaska, California, Hawaii, Oregon, Washington', 'Location.Prefer not to say',
                'Location.South Atlantic - Delaware, District of Columbia, Florida, Georgia, Maryland, North Carolina,South Carolina, Virginia, West Virginia',
                'Location.West North Central - Iowa, Kansas, Minnesota, Missouri, Nebraska, North Dakota, South Dakota',
                'Location.West South Central - Arkansas, Louisiana, Oklahoma, Texas', 'Political party affiliation.Democrat',
                'Political party affiliation.Independent', 'Political party affiliation.Prefer not to say', 'Political party affiliation.Republican',
                'Political party affiliation.Something else', 'Religion.Agnostic', 'Religion.Atheist', 'Religion.Christian', 'Religion.Hindu',
                'Religion.Jewish', 'Religion.Muslim', 'Religion.Other (please specify)', 'Religion.Prefer not to say',
                'Religion.Spiritual but not religious', 'Religion.Unsure', 'education_other', 'deological_other', 'religion_other']
summary = pd.DataFrame([], columns=['worker', 'assignment', 'accept time', 'submit_time', 'score']+survey_head)


def cache_raw(data):
    assignment = data['AssignmentId']
    try:
        with open('data_qualification/'+assignment, 'w', encoding='utf8') as f:
            def converter(o):
                if isinstance(o, datetime.datetime):
                    return o.__str__()
            json.dump(data, f, default=converter)
    except Exception as e:
        print('fail dump json file:', e)

def extract_result(data):
    assignment = data['AssignmentId']
    accept_time = data['AcceptTime']
    submit_time = data['SubmitTime']
    worker = data['WorkerId']

    text = data['Answer']

    ns = '{http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionFormAnswers.xsd}'
    root = ET.fromstring(text)

    submit = {}
    for el in root:
        i = el.find('{}QuestionIdentifier'.format(ns)).text
        j = el.find('{}FreeText'.format(ns)).text
        submit[i] = j

    survey = []
    for i in survey_head:
        if i in submit:
            survey.append(submit[i])
        else:
            survey.append('')

    total = 0
    for i, standard in enumerate(ans1):
        ident = 't{}q1'.format(i)
        key = ident + '.' + standard
        score = 0
        if key in submit and submit[key] == 'true':
            score = 3
        total = total + score

    for i, standard in enumerate(ans3):
        ident = 't{}q3'.format(i)
        if not standard:
            continue
        key = ident + '.' + standard
        score = 0
        if key in submit and submit[key] == 'true':
            score = 2
        total = total + score

    print('===>', worker, total)
    result = [worker, assignment, accept_time, submit_time, total]+survey

    return result

def cache_csv(assignment, result):
    try:
        pd.DataFrame([result], columns=['worker', 'assignment', 'accept time', 'submit_time', 'score']+
                                                survey_head).to_csv('data_qualification/'+assignment+'.csv')
    except Exception as e:
        print(222,e)

def turk_action(worker, assignment, total_score):
    total = total_score

    rrr = client.associate_qualification_with_worker(QualificationTypeId=qualification_id, WorkerId=worker, IntegerValue=total)

    if total >= limit:
        notify_str = email_pass.format(worker=worker, project='Annotate Moral Judgement (Care/Harm) in English Tweets about a Social Issue',
          score=total)

        client.approve_assignment(AssignmentId=assignment, RequesterFeedback=notify_str)
        client.notify_workers(WorkerIds=[worker],
                              Subject='result of your qualification for HIT "{}"'.format('Annotate Moral Judgement (Care/Harm) in English Tweets about a Social Issue'),
                              MessageText=notify_str)
    else:
        notify_str = email_fail.format(worker=worker, project='Annotate Moral Judgement (Care/Harm) in English Tweets about a Social Issue',
          score=total, project_test='[Qualification] Annotate Moral Judgement (Care/Harm) in English Tweets about a Social Issue')

        client.reject_assignment(AssignmentId=assignment, RequesterFeedback=notify_str)
        client.notify_workers(WorkerIds=[worker],
                              Subject='result of your qualification for HIT "{}"'.format('Annotate Moral Judgement (Care/Harm) in English Tweets about a Social Issue'),
                              MessageText=notify_str)


def list_assignments(hit_id):
    global summary
    paginator = client.get_paginator('list_assignments_for_hit')
    response_iterator = paginator.paginate(
        HITId=hit_id,
        AssignmentStatuses=[
            'Submitted',
        ]
    )

    for r in response_iterator:
        for data in r['Assignments']:
            cache_raw(data)

            result = extract_result(data)

            worker, assignment, score = result[0], result[1], result[4]

            cache_csv(assignment, result)

            turk_action(worker, assignment, score)

            summary = summary.append(pd.DataFrame([result],
                                        columns=['worker', 'assignment', 'accept time', 'submit_time', 'score']+survey_head),
                            ignore_index=True)
    print(summary.to_string(columns=['worker', 'assignment', 'accept time', 'submit_time', 'score']))

    total = summary['worker'].count()
    pass_total = summary.loc[summary['score']>=85, 'worker'].count()
    print('#### {}/{} ###'.format(pass_total, total))


def loop(hit_id):
    while True:
        try:
            list_assignments(hit_id)
        except Exception as e:
            print('exception from list assignments:', e)
        import time
        time.sleep(10)


try:
    loop(hit_id)
finally:
    summary.to_csv('data_qualification/summary.'+hit_id+'.csv')

