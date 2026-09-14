import ast
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DAG_PATH = REPOSITORY_ROOT / "airflow" / "dags" / "ETL_toll_data.py"


class DagStructureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = DAG_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source, filename=str(DAG_PATH))

    def test_expected_tasks_are_declared(self):
        task_ids = []
        for node in ast.walk(self.tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "BashOperator"
            ):
                continue
            task_id = next(
                (
                    keyword.value.value
                    for keyword in node.keywords
                    if keyword.arg == "task_id"
                    and isinstance(keyword.value, ast.Constant)
                ),
                None,
            )
            if task_id is not None:
                task_ids.append(task_id)

        self.assertEqual(
            task_ids,
            [
                "unzip_data",
                "validate_input_data",
                "extract_data_from_csv",
                "extract_data_from_tsv",
                "extract_data_from_fixed_width",
                "consolidate_data",
                "transform_data",
                "load_data",
            ],
        )

    def test_dag_disables_historical_backfill(self):
        dag_calls = [
            node
            for node in ast.walk(self.tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "DAG"
        ]
        self.assertEqual(len(dag_calls), 1)
        catchup = next(
            keyword.value
            for keyword in dag_calls[0].keywords
            if keyword.arg == "catchup"
        )
        self.assertIsInstance(catchup, ast.Constant)
        self.assertFalse(catchup.value)

    def test_pipeline_ends_with_load(self):
        self.assertIn(
            "unzip_data >> validate_input_data >> [",
            self.source,
        )
        self.assertIn(
            "consolidate_data >> transform_data >> load_data",
            self.source,
        )

    def test_input_validation_checks_all_sources(self):
        self.assertIn('"{WORK_DIR}/vehicle-data.csv"', self.source)
        self.assertIn('"{WORK_DIR}/tollplaza-data.tsv"', self.source)
        self.assertIn('"{WORK_DIR}/payment-data.txt"', self.source)
        self.assertIn('[[ ! -s "$source_file" ]]', self.source)

    def test_fixed_width_contract_is_encoded(self):
        self.assertIn("substr($0, 1, 10)", self.source)
        self.assertIn("substr($0, 11, 10)", self.source)


if __name__ == "__main__":
    unittest.main()
