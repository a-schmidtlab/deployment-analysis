"""Regenerate ``examples/sample_data.csv`` (synthetic, deterministic)."""

from pathlib import Path

from deployment_analyzer.sampledata import generate_export

OUTPUT = Path(__file__).resolve().parent.parent / "examples" / "sample_data.csv"

if __name__ == "__main__":
    frame = generate_export(n=3000, start="2025-02-03", days=21, seed=7)
    frame.to_csv(OUTPUT, sep=";", index=False, encoding="utf-8")
    print(f"{len(frame)} rows written to {OUTPUT}")
