Price data from vendors often contains errors that need to be identified and investigated. There are three types of issues:

 - Missing values (‘missing value’)
 - Stale values that are unchanged for more than 1 week (‘stale value’)
 - Outliers, i.e. values that are far away from nearby values (‘outlier’)

We implement function def check_file_data(file_path: str) -> List[tuple[date, float, str]]
to detect *all* of the erroneous data. Avoiding false positives is secondary, less
than 20 per series is acceptable.
There are some CSVs of sample raw and clean prices for different instruments types. There
are 2 columns in each file, Date and Price, with a header row. Dates are in the format dd/mm/yyyy.

We built some test to verify what we are doing is correct compare with *_clean.csv