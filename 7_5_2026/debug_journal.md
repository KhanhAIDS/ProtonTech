# Debug Journal

## Bug 1: Wrong CSV delimiter
- **Original problem:** The script used `csv.reader(f, delimiter='\t')`.
- **Why it failed:** `extracted_features_final.csv` is comma-separated, not tab-separated. With the wrong delimiter, each row was not split into the expected 26 columns, so column lookups like `row[24]` and `row[25]` could fail or produce incorrect data.
- **Fix:** Switched the reader to the default comma delimiter by using `csv.reader(f)`.

## Bug 2: Comparing score values as strings
- **Original problem:** The code checked `if row[25] >= args.threshold:`.
- **Why it failed:** Both values were strings. String comparison is lexicographic, not numeric, so the threshold logic could accept or reject the wrong rows.
- **Fix:** Converted the score and threshold to floats before comparing them.

## Bug 3: Threshold argument was treated as text
- **Original problem:** `argparse` returned `args.threshold` as a string because no type was set.
- **Why it failed:** The script expected a numeric threshold for filtering, but it was comparing against a string value.
- **Fix:** Converted `args.threshold` to `float` inside `process_and_stats()` before using it.

## Bug 4: Adding string values to numeric totals
- **Original problem:** The code did `total_score = total_score + row[25]` and `total_sym_index = total_sym_index + row[24]`.
- **Why it failed:** `row[25]` and `row[24]` were strings, so the script would either raise a type error or produce invalid results if the code path was changed later.
- **Fix:** Converted both fields to floats before adding them to the totals.

## Bug 5: Output formatting used string concatenation with numbers
- **Original problem:** The code printed `len(filtered_data)`, `avg_score`, and `avg_sym` by concatenating them directly to strings.
- **Why it failed:** Python does not concatenate strings with integers or floats without explicit conversion, so the script would raise a `TypeError`.
- **Fix:** Wrapped the numeric values in `str()` when printing them.

## Bug 6: Average variables could be undefined when no rows matched
- **Original problem:** `avg_score` and `avg_sym` were only assigned inside the `if len(filtered_data) > 0:` block.
- **Why it failed:** If no rows passed the filter, the later `print()` calls would reference variables that had never been set, causing an `UnboundLocalError`.
- **Fix:** Set both averages to `0.0` in the no-match case.

## Bug 7: Filtering state was not reset before each run
- **Original problem:** `filtered_data`, `total_score`, and `total_sym_index` were global values that were never reset inside the processing function.
- **Why it failed:** If the function were called more than once in the same Python process, old results would leak into the new run.
- **Fix:** Reset the globals to empty / zero values at the start of `process_and_stats()`.
