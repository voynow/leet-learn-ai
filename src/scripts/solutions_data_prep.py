import json
import os
from collections import defaultdict

import pandas as pd
from datasets import load_dataset


def get_diff(str_a, str_b):
    a = str_a.splitlines()
    b = str_b.splitlines()
    return '\n'.join([x for x in a if x not in b])


def preprocess_dataset(dataset):
    df = pd.DataFrame(dataset['train'])
    df.index = df['id']
    df.drop('id', axis=1, inplace=True)
    df['problem'] = df.apply(lambda x: get_diff(x.code_with_problem, x.code_only), axis=1)
    df['name'] = df.apply(lambda x: x.code_with_data.splitlines()[0].replace("# ", ""), axis=1)
    df['difficulty'] = df.apply(lambda x: x.code_with_data.splitlines()[2].replace("# ", ""), axis=1)
    df.drop(['code_with_problem', 'code_with_data'], axis=1, inplace=True)
    df.rename(columns={'code_only': 'code', 'explanation_only': 'explanation'}, inplace=True)
    return df


def reorient_json(input_path, output_path):
    with open(input_path, 'r') as f_in:
        data = json.load(f_in)['data']

    reoriented_data = defaultdict(list)
    for item in data:
        for key, value in item.items():
            reoriented_data[key].append(value)

    with open(output_path, 'w') as f_out:
        json.dump(dict(reoriented_data), f_out)


def main():
    dataset = load_dataset('mhhmm/leetcode-solutions-python')
    df = preprocess_dataset(dataset)

    csv_path = 'data/solutions.csv'
    intermediate_json_path = 'data/solutions_intermediate.json'
    final_json_path = 'data/solutions.json'

    df.to_csv(csv_path, index=False)
    df.to_json(intermediate_json_path, orient='table', index=False)
    reorient_json(intermediate_json_path, final_json_path)

    # Remove intermediate files
    os.remove(csv_path)
    os.remove(intermediate_json_path)


if __name__ == "__main__":
    main()
