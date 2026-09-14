import subprocess
import tempfile
import unittest
from pathlib import Path


FIXED_WIDTH_AWK = r'''
  function trim(value) {
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
    return value
  }
  { print trim(substr($0, 1, 10)) "," trim(substr($0, 11, 10)) }
'''

TRANSFORM_AWK = r'''BEGIN { OFS="," } { $2=toupper($2); print }'''

ROW_ALIGNMENT_CHECK = r'''
  set -euo pipefail
  csv_rows=$(wc -l < ./data/csv_data.csv)
  tsv_rows=$(wc -l < ./data/tsv_data.csv)
  fixed_width_rows=$(wc -l < ./data/fixed_width_data.csv)
  if [[ "$csv_rows" -ne "$tsv_rows" || "$csv_rows" -ne "$fixed_width_rows" ]]; then
    exit 1
  fi
'''


class ShellTransformationTest(unittest.TestCase):
    def test_fixed_width_extraction_trims_fields_and_crlf(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "payment-data.txt"
            source.write_bytes(b"PAYMENT01 VEHICLE001\r\n")

            result = subprocess.run(
                ["awk", FIXED_WIDTH_AWK, str(source)],
                check=True,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.stdout, "PAYMENT01,VEHICLE001\n")

    def test_vehicle_type_transformation_targets_field_two(self):
        result = subprocess.run(
            ["awk", "-F,", TRANSFORM_AWK],
            input="vehicle-001,sedan,ABC-123,plaza-01\n",
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            result.stdout,
            "vehicle-001,SEDAN,ABC-123,plaza-01\n",
        )

    def test_row_alignment_check_rejects_mismatched_files(self):
        with tempfile.TemporaryDirectory() as directory:
            data_directory = Path(directory) / "data"
            data_directory.mkdir()
            (data_directory / "csv_data.csv").write_text("row-1\nrow-2\n")
            (data_directory / "tsv_data.csv").write_text("row-1\n")
            (data_directory / "fixed_width_data.csv").write_text(
                "row-1\nrow-2\n"
            )

            result = subprocess.run(
                ["bash", "-c", ROW_ALIGNMENT_CHECK],
                cwd=directory,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
