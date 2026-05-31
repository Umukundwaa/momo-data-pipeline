import time
import sys
import os
import json

# Import parser
from etl.parse_xml import parse_xml

# LOAD DATA

XML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "../modified_sms_v2.xml")

print("Loading transactions...")
transactions_list = parse_xml(XML_FILE)
transactions_dict = {t["id"]: t for t in transactions_list}
print(f"Loaded {len(transactions_list)} transactions\n")



# LINEAR SEARCH — O(n)

def linear_search(data_list, target_id):
    """
    Linear Search Algorithm — Time Complexity: O(n)

    Scans through every element in the list from start to finish
    until the target ID is found or the list ends.
    Best case:  O(1) — target is the first element
    Worst case: O(n) — target is the last element or not found
    Average:    O(n/2) — target is somewhere in the middle
    """
    for transaction in data_list:
        if transaction["id"] == target_id:
            return transaction
    return None



#  DICTIONARY LOOKUP — O(1)

def dictionary_lookup(data_dict, target_id):
    """
    Dictionary Lookup — Time Complexity: O(1)
    Uses a Python dictionary (hash map) to jump directly to the
    record using the ID as a key. No scanning needed.
    Best case:  O(1)
    Worst case: O(1) — always instant regardless of dataset size
    Average:    O(1)
    """
    return data_dict.get(target_id, None)

# COMPARISON TEST BOTH ON 20+ RECORDS

def measure_time(func, *args, runs=1000):
    """
    Measure average execution time of a function over multiple runs.
    Returns time in microseconds.
    """
    start = time.perf_counter()
    for _ in range(runs):
        result = func(*args)
    end = time.perf_counter()
    avg_time = ((end - start) / runs) * 1_000_000  # convert to microseconds
    return avg_time, result


def run_comparison():
    """
    Run comparison between linear search and dictionary lookup
    on at least 20 different transaction IDs.
    """
    print("=" * 65)
    print("  DSA COMPARISON: Linear Search vs Dictionary Lookup")
    print("  Team Nexus | MoMo Data Pipeline")
    print("=" * 65)
    print(f"\nDataset size: {len(transactions_list)} transactions\n")

    # Test IDs spread across the dataset — at least 20
    test_ids = [1, 50, 100, 200, 300, 400, 500, 600, 700, 800,
                900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1691, 999]

    print(f"{'ID':>6} | {'Linear (μs)':>12} | {'Dict (μs)':>12} | {'Speedup':>10} | {'Found':>6}")
    print("-" * 65)

    linear_times = []
    dict_times = []

    for tid in test_ids:
        linear_time, linear_result = measure_time(
            linear_search, transactions_list, tid)
        dict_time, dict_result = measure_time(
            dictionary_lookup, transactions_dict, tid)

        linear_times.append(linear_time)
        dict_times.append(dict_time)

        speedup = linear_time / dict_time if dict_time > 0 else float('inf')
        found = "Yes" if linear_result else "No"

        print(f"{tid:>6} | {linear_time:>12.4f} | {dict_time:>12.4f} | "
              f"{speedup:>9.1f}x | {found:>6}")

    print("-" * 65)

    avg_linear = sum(linear_times) / len(linear_times)
    avg_dict = sum(dict_times) / len(dict_times)
    avg_speedup = avg_linear / avg_dict if avg_dict > 0 else float('inf')

    print(f"\n{'AVERAGES':>6} | {avg_linear:>12.4f} | {avg_dict:>12.4f} | "
          f"{avg_speedup:>9.1f}x |")

    print(f"""
{'=' * 65}
RESULTS SUMMARY
{'=' * 65}
Linear Search average time : {avg_linear:.4f} microseconds
Dictionary Lookup avg time : {avg_dict:.4f} microseconds
Dictionary is faster by    : {avg_speedup:.1f}x on average

EXPLANATION:
Linear Search scans every record from position 0 until it finds
the target. For a dataset of {len(transactions_list)} records, it may check
up to {len(transactions_list)} records in the worst case — O(n) complexity.

Dictionary Lookup uses a hash map (Python dict). Python computes
a hash of the key (ID) and jumps directly to the memory address
where the value is stored. This takes constant time regardless
of dataset size — O(1) complexity.

REFLECTION:
Why is dictionary lookup faster?
  - Linear search: time grows WITH the dataset size
  - Dictionary lookup: time stays CONSTANT no matter how big the dataset

Other data structures that could improve search efficiency:
  1. Binary Search Tree (BST) — O(log n) search on sorted data
  2. Binary Search on sorted list — O(log n) if list is pre-sorted by ID
  3. Hash Table — same as dict, O(1) average
  4. Trie — O(k) where k is key length, great for text/string searches
{'=' * 65}
""")

    # Export results as JSON for documentation
    results = {
        "dataset_size": len(transactions_list),
        "test_ids": test_ids,
        "average_linear_search_microseconds": round(avg_linear, 4),
        "average_dictionary_lookup_microseconds": round(avg_dict, 4),
        "average_speedup": round(avg_speedup, 1),
        "conclusion": "Dictionary lookup is significantly faster than linear search for large datasets"
    }

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "dsa_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to dsa/dsa_results.json")


if __name__ == "__main__":
    run_comparison()