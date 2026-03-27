# Required library: numpy
# Install using: pip install numpy

import numpy as np
import csv

def load_csv(file_path):
    """
    Load CSV into a structured numpy array.
    Assumes CSV has header: id,tag,year,company_id,formula_sign
    """
    data = np.genfromtxt(file_path, delimiter=',', dtype=None, encoding='utf-8', names=True)
    return data

def compare_balances(old_file, new_file, output_file):
    old_data = load_csv(old_file)
    new_data = load_csv(new_file)

    # Create dictionaries for fast lookup using (id, tag, year, company_id) as key
    old_dict = { (row['id'], row['tag'], row['year'], row['company_id']): row['formula_sign'] for row in old_data }
    new_dict = { (row['id'], row['tag'], row['year'], row['company_id']): row['formula_sign'] for row in new_data }

    # Find differences
    differences = []
    all_keys = set(old_dict.keys()).union(new_dict.keys())

    for key in all_keys:
        old_balance = old_dict.get(key, None)
        new_balance = new_dict.get(key, None)
        if old_balance != new_balance:
            differences.append({
                'id': key[0],
                'tag': key[1],
                'year': key[2],
                'company_id': key[3],
                'formula_sign_old': old_balance,
                'formula_sign_new': new_balance
            })

    # Write differences to CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id','tag','year','company_id','formula_sign_old','formula_sign_new'])
        writer.writeheader()
        writer.writerows(differences)

    print(f"Differences saved to {output_file}")
    print(f"Total differences found: {len(differences)}")

if __name__ == "__main__":
    old_file_path = "tax_tags_18.csv"   # Replace with your file path
    new_file_path = "tax_tags_19.csv"   # Replace with your file path
    output_file_path = "balance_difference_numpy.csv"

    compare_balances(old_file_path, new_file_path, output_file_path)