from datasets import load_dataset
import pandas as pd


def get_diff(str_a, str_b):
    """perform line by line str_a subtract str_b"""
    a = str_a.splitlines()
    b = str_b.splitlines()
    return '\n'.join([x for x in a if x not in b])


def main():

    dataset = load_dataset('mhhmm/leetcode-solutions-python')
    df = pd.DataFrame(dataset['train'])

    # update index
    df.index = df['id']
    df.drop('id', axis=1, inplace=True)

    # add new columns
    df['problem'] = df.apply(lambda x: get_diff(x.code_with_problem, x.code_only), axis=1)
    df['name'] = df.apply(lambda x: x.code_with_data.splitlines()[0].replace("# ", ""), axis=1)
    df['difficulty'] = df.apply(lambda x: x.code_with_data.splitlines()[2].replace("# ", ""), axis=1)

    # cleanup columns
    df.drop(['code_with_problem', 'code_with_data'], axis=1, inplace=True)
    df.rename(columns={'code_only': 'code', 'explanation_only': 'explaination'}, inplace=True)

    df.to_csv('data/solutions.csv', index=False)


main()