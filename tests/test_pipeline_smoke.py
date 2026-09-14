import subprocess
import tempfile
import unittest
from pathlib import Path


PIPELINE_SCRIPT = r'''
set -euo pipefail

cut -d',' -f1-4 "$WORK_DIR/vehicle-data.csv" \
  | sed 's/\r$//' > "$DAGS_DIR/data/csv_data.csv"
cut -f5-7 "$WORK_DIR/tollplaza-data.tsv" \
  | tr '\t' ',' \
  | sed 's/\r$//' > "$DAGS_DIR/data/tsv_data.csv"
awk '
  function trim(value) {
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
    return value
  }
  { print trim(substr($0, 1, 10)) "," trim(substr($0, 11, 10)) }
' "$WORK_DIR/payment-data.txt" > "$DAGS_DIR/data/fixed_width_data.csv"

csv_rows=$(wc -l < "$DAGS_DIR/data/csv_data.csv")
tsv_rows=$(wc -l < "$DAGS_DIR/data/tsv_data.csv")
fixed_width_rows=$(wc -l < "$DAGS_DIR/data/fixed_width_data.csv")
[[ "$csv_rows" -eq "$tsv_rows" && "$csv_rows" -eq "$fixed_width_rows" ]]

paste -d',' \
  "$DAGS_DIR/data/csv_data.csv" \
  "$DAGS_DIR/data/tsv_data.csv" \
  "$DAGS_DIR/data/fixed_width_data.csv" \
  > "$DAGS_DIR/data/extracted_data.csv"

awk -F',' 'NF == 9' "$DAGS_DIR/data/extracted_data.csv" \
  > "$DAGS_DIR/data/validated_data.csv"
awk -F',' 'BEGIN { OFS="," } {$2=toupper($2); print}' \
  "$DAGS_DIR/data/validated_data.csv" \
  > "$DAGS_DIR/staging/transformed_data.csv"
awk -F',' 'NF == 9 && $2 == toupper($2)' \
  "$DAGS_DIR/staging/transformed_data.csv" \
  > "$DAGS_DIR/staging/validated_transformed_data.csv"

FINAL_FILE="$DAGS_DIR/staging/final/transformed_data.csv"
TEMP_FILE="$FINAL_FILE.tmp"
mkdir -p "$DAGS_DIR/staging/final"
cp "$DAGS_DIR/staging/validated_transformed_data.csv" "$TEMP_FILE"
mv -- "$TEMP_FILE" "$FINAL_FILE"
'''


class PipelineSmokeTest(unittest.TestCase):
    def test_two_record_fixture_reaches_final_staging(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dags_dir = root / "dags"
            data_dir = dags_dir / "data"
            staging_dir = dags_dir / "staging"
            work_dir = root / "work"
            data_dir.mkdir(parents=True)
            work_dir.mkdir()

            (work_dir / "vehicle-data.csv").write_text(
                "v1,sedan,ABC-123,plaza-01\n"
                "v2,truck,XYZ-789,plaza-02\n",
                encoding="utf-8",
            )
            (work_dir / "tollplaza-data.tsv").write_text(
                "a\tb\tc\td\t2\tplaza-01\tcode-01\n"
                "a\tb\tc\td\t4\tplaza-02\tcode-02\n",
                encoding="utf-8",
            )
            (work_dir / "payment-data.txt").write_text(
                "PAYMENT001VEHICLE001\r\n"
                "PAYMENT002VEHICLE002\r\n",
                encoding="utf-8",
            )
            staging_dir.mkdir()

            result = subprocess.run(
                ["bash", "-c", PIPELINE_SCRIPT],
                env={
                    "DAGS_DIR": str(dags_dir),
                    "WORK_DIR": str(work_dir),
                },
                check=True,
                capture_output=True,
                text=True,
            )

            final_file = staging_dir / "final" / "transformed_data.csv"
            self.assertEqual(
                final_file.read_text(encoding="utf-8"),
                "v1,SEDAN,ABC-123,plaza-01,2,plaza-01,code-01,PAYMENT001,VEHICLE001\n"
                "v2,TRUCK,XYZ-789,plaza-02,4,plaza-02,code-02,PAYMENT002,VEHICLE002\n",
            )
            self.assertFalse(final_file.with_suffix(".csv.tmp").exists())
            self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
