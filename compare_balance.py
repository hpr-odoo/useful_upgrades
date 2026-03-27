import numpy as np
import csv
import argparse

def load_csv(file_path):
    """
    Load CSV into a structured numpy array.
    Handles both column names:
      - 'balance' (production)
      - 'formula_sign' (upgraded)
    """
    return np.genfromtxt(file_path, delimiter=',', dtype=None, encoding='utf-8', names=True)


def compare_balances(old_file, new_file, output_file):
    old_data = load_csv(old_file)
    new_data = load_csv(new_file)

    # Create dictionaries for fast lookup using id as key
    old_dict = {row['id']: float(row['balance']) for row in old_data}
    new_dict = {row['id']: float(row['formula_sign']) for row in new_data}

    # Metadata lookup
    old_meta = {
        row['id']: {'tag': row['tag'], 'year': row['year'], 'company_id': row['company_id']}
        for row in old_data
    }
    new_meta = {
        row['id']: {'tag': row['tag'], 'year': row['year'], 'company_id': row['company_id']}
        for row in new_data
    }

    all_ids    = set(old_dict.keys()).union(new_dict.keys())
    only_old   = set(old_dict.keys()) - set(new_dict.keys())
    only_new   = set(new_dict.keys()) - set(old_dict.keys())
    common_ids = set(old_dict.keys()).intersection(new_dict.keys())

    # --- Find changed lines among common IDs ---
    changed = []
    identical_count = 0

    for id_ in sorted(common_ids):
        old_bal = old_dict[id_]
        new_bal = new_dict[id_]
        diff    = round(new_bal - old_bal, 2)

        if diff == 0.0:
            identical_count += 1
            continue

        # Classify
        if old_bal > 0 and new_bal < 0:
            status = 'SIGN FLIP (+->-)'
        elif old_bal < 0 and new_bal > 0:
            status = 'WRONG DIRECTION FLIP (->+) !!!'
        else:
            status = 'VALUE CHANGED'

        meta = old_meta.get(id_) or new_meta.get(id_)
        changed.append({
            'id'          : id_,
            'tag'         : meta['tag'],
            'year'        : meta['year'],
            'company_id'  : meta['company_id'],
            'balance_old' : old_bal,
            'balance_new' : new_bal,
            'difference'  : diff,
            'status'      : status
        })

    # --- Missing in new ---
    for id_ in sorted(only_old):
        meta = old_meta[id_]
        changed.append({
            'id'          : id_,
            'tag'         : meta['tag'],
            'year'        : meta['year'],
            'company_id'  : meta['company_id'],
            'balance_old' : old_dict[id_],
            'balance_new' : 'MISSING',
            'difference'  : 'N/A',
            'status'      : 'MISSING IN NEW'
        })

    # --- Missing in old ---
    for id_ in sorted(only_new):
        meta = new_meta[id_]
        changed.append({
            'id'          : id_,
            'tag'         : meta['tag'],
            'year'        : meta['year'],
            'company_id'  : meta['company_id'],
            'balance_old' : 'MISSING',
            'balance_new' : new_dict[id_],
            'difference'  : 'N/A',
            'status'      : 'MISSING IN OLD'
        })

    # --- Write CSV ---
    fieldnames = ['id', 'tag', 'year', 'company_id', 'balance_old', 'balance_new', 'difference', 'status']
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(changed)

    # --- Totals ---
    total_old = sum(old_dict.values())
    total_new = sum(new_dict.values())
    net_diff  = round(total_new - total_old, 2)

    sign_flip     = sum(1 for d in changed if 'SIGN FLIP' in str(d['status']))
    wrong_flip    = sum(1 for d in changed if 'WRONG' in str(d['status']))
    value_changed = sum(1 for d in changed if d['status'] == 'VALUE CHANGED')
    missing_new   = sum(1 for d in changed if d['status'] == 'MISSING IN NEW')
    missing_old   = sum(1 for d in changed if d['status'] == 'MISSING IN OLD')

    # --- Print summary ---
    print(f"{'='*55}")
    print(f"  OVERVIEW")
    print(f"{'='*55}")
    print(f"  Old file                    : {old_file}")
    print(f"  New file                    : {new_file}")
    print(f"  Output file                 : {output_file}")
    print(f"{'='*55}")
    print(f"  Total lines compared        : {len(all_ids)}")
    print(f"  Identical balance           : {identical_count}")
    print(f"  Changed balance             : {len(changed)}")
    print(f"  Actual diff (non-sign-flip) : {value_changed + missing_new + missing_old}")
    print(f"  Total balance (old)         : {total_old:,.2f}")
    print(f"  Total balance (new)         : {total_new:,.2f}")
    print(f"  Net difference              : {net_diff:,.2f}")
    print(f"{'='*55}")
    print(f"  CHANGED LINES BREAKDOWN")
    print(f"{'='*55}")
    print(f"  Sign flip (+->-)            : {sign_flip}")
    print(f"  Wrong direction flip (->+)  : {wrong_flip}  !!!")
    print(f"  Value changed               : {value_changed}")
    print(f"  Missing in new file         : {missing_new}")
    print(f"  Missing in old file         : {missing_old}")
    print(f"{'='*55}")
    print(f"\n  {'ID':<12} {'balance_old':>12} {'balance_new':>12} {'difference':>12}  STATUS")
    print(f"  {'-'*70}")
    for d in changed:
        print(
            f"  {str(d['id']):<12} "
            f"{str(d['balance_old']):>12} "
            f"{str(d['balance_new']):>12} "
            f"{str(d['difference']):>12}  "
            f"{d['status']}"
        )
    print(f"\n  Output saved to: {output_file}")
    print(f"{'='*55}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Compare balance between two CSV files and find differences.'
    )
    parser.add_argument('old_file',    help='Path to the OLD csv file  (e.g. production.csv)')
    parser.add_argument('new_file',    help='Path to the NEW csv file  (e.g. upgraded.csv)')
    parser.add_argument('output_file', help='Path to the OUTPUT csv file (e.g. balance_diff.csv)')

    args = parser.parse_args()

    compare_balances(args.old_file, args.new_file, args.output_file)
