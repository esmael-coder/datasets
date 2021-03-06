import re
import pandas as pd
import xmltodict

# Temporal Rules


def first_rule(requirement, sutime):
    """
    First Rule
    ∀[\exp]<DURATION>, exp ← within
    """
    if sutime['TIMEX3']['@type'] == 'DURATION':
        expressions = ['no longer than', 'in under', 'no more than',
                       'not be more than', 'no later', ' in ',
                       'for less than', 'at a maximum']
        for exp in expressions:
            if exp in requirement:
                if exp is ' in ':  # Prevent unintended replacement of in
                    requirement = requirement.replace(exp, ' within ')
                else:
                    requirement = requirement.replace(exp, 'within')

    return requirement


def second_rule(requirement, sutime):
    """
    Second rule 2.0
    ∀[\DURATION\TIME\DATE]+ ← alltimes
    """
    expressions = ['24 hours per day 365 days per year',
                   '24 hours per day seven days per week', '24 hour']

    for exp in expressions:
        if exp in requirement:
            requirement = requirement.replace(exp, 'alltimes')

    # if sutime['TIMEX3']['@type'] == 'DURATION' or \
    #   sutime['TIMEX3']['@type'] == 'TIME' or \
    #   sutime['TIMEX3']['@type'] == 'DATE':
    #    content = sutime['TIMEX3']['#text']
    #    if 'alltimes' not in requirement:
    #        requirement = requirement.replace(content, 'alltimes')
    #    else:
    #        requirement = requirement.replace(content, '')
    return requirement


def third_rule(requirement, sutime):
    """
    Third rule
    within <DURATION> ← fast
    if <DURATION> == [\seconds\minutes\second\minute]
    """
    if sutime['TIMEX3']['@type'] == 'DURATION':
        requirement = re.sub(r'(within )*(\d+(?:\.\d+)? )*(second)+s?', 'fast', requirement)
        requirement = re.sub(r'(within )*(\d+(?:\.\d+)? )*(minute)+s?', 'fast', requirement)

    return requirement


def fourth_rule(requirement, sutime):
    """
    Fourth rule 2.0
    {timely, quick} || [\positive adj \time] ← fast
    """
    if 'timely' in requirement:
        requirement = requirement.replace('timely', 'fast')
    if 'quickly' in requirement:
        requirement = requirement.replace('quickly', 'fast')
    return requirement


def fifth_rule(requirement, sutime):
    """
    Fifth rule 2.0
    [8-9][0-9][\.?[0-9]?%?][IN | SET]*time ← alltimes
    """
    requirement = re.sub(r'[8-9][0-9][\.?[0-9]?% of the time?',  # > 80% of the time
                         'alltimes', requirement)
    requirement = re.sub(r'[8-9][0-9][\.?[0-9]?% up time?',  # > 80% uptime
                         'uninterrupted uptime', requirement)
    if sutime['TIMEX3']['@type'] == 'IN' or \
       sutime['TIMEX3']['@type'] == 'SET':
        requirement = requirement.replace(
            sutime['TIMEX3']['#text'], 'alltimes')
    return requirement

# Percentage Rule


def percentage_rule(requirement):
    # 100% → all
    requirement = re.sub(r'100%', 'all', requirement)
    # >= 50% → most
    requirement = re.sub(
        r'(([5-9]\d|[1-9]\d{2,})|(\.\d+))+?%', 'most', requirement)
    # < 50% → little
    requirement = re.sub(r'(\d+(\.\d+)?%)', 'little', requirement)
    return requirement


if __name__ == "__main__":

    requirements = open('pre-tag.txt', "r").readlines()

    # Read Time Taggs
    temp_tags = pd.read_csv('./temporal-tags.csv')

    # Applying Temporal Rules

    for index, row in temp_tags.iterrows():
        sutime = xmltodict.parse(row['tag'])
        expression = second_rule(
            requirements[row['line']],
            sutime
        )
        requirements[row['line']] = expression

    for index, row in temp_tags.iterrows():
        sutime = xmltodict.parse(row['tag'])
        expression = first_rule(
            requirements[row['line']],
            sutime
        )
        requirements[row['line']] = expression

    for index, row in temp_tags.iterrows():
        sutime = xmltodict.parse(row['tag'])
        expression = third_rule(
            requirements[row['line']],
            sutime
        )
        requirements[row['line']] = expression

    for index, row in temp_tags.iterrows():
        sutime = xmltodict.parse(row['tag'])
        expression = fourth_rule(
            requirements[row['line']],
            sutime
        )
        requirements[row['line']] = expression

    for index, row in temp_tags.iterrows():
        sutime = xmltodict.parse(row['tag'])
        expression = fifth_rule(
            requirements[row['line']],
            sutime
        )
        requirements[row['line']] = expression

    # Percentages normalization

    for i in range(len(requirements)):
        expression = percentage_rule(requirements[i])
        requirements[i] = expression

    # Save output

    with open('../time_normalized.txt', 'w') as f:
        for line in requirements:
            f.write("%s" % line)
