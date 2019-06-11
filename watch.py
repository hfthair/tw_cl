import json
import datetime
import xml.etree.ElementTree as ET

import boto3
import pandas as pd

hit_id = '33J5JKFMK66H0U58GGTZUOVUR343Q7'
qualification_id = '3ZSPHI510K37QY5MX5XWD46WRCSJII'
limit = 0


client = boto3.client('mturk',
                      region_name='us-east-1',
                      endpoint_url='https://mturk-requester-sandbox.us-east-1.amazonaws.com')


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


survey_head = ['Age.30-39', 'Age.40-49', 'Age.50-59', 'Age.60+', 'Age.Prefer not to say', 'Age.Under 30', "Education.Bachelor's degree", 'Education.College degree', 'Education.Doctorate degree', 'Education.High school diploma', 'Education.Less than high school degree', "Education.Master's degree", 'Education.Other (please specify)', 'Education.Prefer not to say', 'Gender.Female', 'Gender.Male', 'Gender.Non-binary', 'Gender.Prefer not to say', 'Ideological preferences.Conservative', 'Ideological preferences.Liberal', 'Ideological preferences.Moderate', 'Ideological preferences.Other (please specify)', 'Ideological preferences.Prefer not to say', 'Ideological preferences.Unsure', 'Location.East North Central - Illinois, Indiana, Michigan, Ohio, Wisconsin', 'Location.East South Central - Alabama, Kentucky, Mississippi, Tennessee', 'Location.Middle Atlantic - New Jersey, New York, Pennsylvania', 'Location.Mountain - Arizona, Colorado, Idaho, Montana, Nevada, New Mexico, Utah, Wyoming',
               'Location.New England - Connecticut, Maine, Massachusetts, New Hampshire, Rhode Island, Vermont', 'Location.Pacific - Alaska, California, Hawaii, Oregon, Washington', 'Location.Prefer not to say', 'Location.South Atlantic - Delaware, District of Columbia, Florida, Georgia, Maryland, North Carolina, South Carolina, Virginia, West Virginia', 'Location.West North Central - Iowa, Kansas, Minnesota, Missouri, Nebraska, North Dakota, South Dakota', 'Location.West South Central - Arkansas, Louisiana, Oklahoma, Texas', 'Political party affiliation.Democrat', 'Political party affiliation.Independent', 'Political party affiliation.Prefer not to say', 'Political party affiliation.Republican', 'Political party affiliation.Something else', 'Religion.Agnostic', 'Religion.Atheist', 'Religion.Christian', 'Religion.Hindu', 'Religion.Jewish', 'Religion.Muslim', 'Religion.Other (please specify)', 'Religion.Prefer not to say', 'Religion.Spiritual but not religious', 'Religion.Unsure', 'education_other', 'deological_other', 'religion_other']


def process_data(data):
    assignment = data['AssignmentId']
    try:
        with open('data_qualification/'+assignment, 'w', encoding='utf8') as f:
            def converter(o):
                if isinstance(o, datetime.datetime):
                    return o.__str__()
            json.dump(data, f, default=converter)
    except Exception as e:
        print('fail dump json file', e)

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
    #     print(key, submit[key], score)
        total = total + score

    for i, standard in enumerate(ans3):
        ident = 't{}q3'.format(i)
        if not standard:
            continue
        key = ident + '.' + standard
        score = 0
        if key in submit and submit[key] == 'true':
            score = 2
    #     print(key, submit[key], score)
        total = total + score

    try:
        pd.DataFrame([[worker, assignment, accept_time, submit_time, total]+survey],
                     columns=['work', 'assignment', 'accept time', 'submit_time', 'score'] +
                     survey_head).to_csv('data_qualification/'+assignment+'.csv')
    except Exception as e:
        print(222, e)

    print('===>', worker, total)

    rrr = client.associate_qualification_with_worker(
        QualificationTypeId=qualification_id, WorkerId=worker, IntegerValue=total)

    if total > limit:
        client.approve_assignment(AssignmentId=assignment)
        client.notify_workers(WorkerIds=[worker],
                              Subject='Nofity of score',
                              MessageText='This is the message to notify you that you finished..., your score: {}'.format(total))
    else:
        client.notify_workers(WorkerIds=[worker],
                              Subject='Nofity of score',
                              MessageText='This is the message to notify you that you finished..., your score: {}'.format(total))


def list_assignments(hit_id):
    paginator = client.get_paginator('list_assignments_for_hit')
    response_iterator = paginator.paginate(
        HITId=hit_id,
        AssignmentStatuses=[
            'Submitted',
        ]
    )

    for r in response_iterator:
        for data in r['Assignments']:
            process_data(data)


def loop(hit_id):
    while True:
        try:
            list_assignments(hit_id)
        except Exception as e:
            print('exception from list assignments', e)
        import time
        time.sleep(10)


loop(hit_id)
