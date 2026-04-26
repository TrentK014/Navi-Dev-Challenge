import json
import sqlite3
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SRC = os.path.join(DATA_DIR, "seed_data.json")
DB = os.path.join(DATA_DIR, "seed.db")

SCHEMA = """
CREATE TABLE machines (
  code TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT
);

CREATE TABLE products (
  code TEXT PRIMARY KEY,
  product_group TEXT
);

CREATE TABLE routes (
  product_code TEXT NOT NULL,
  bom_code TEXT NOT NULL PRIMARY KEY,
  version INTEGER NOT NULL,
  FOREIGN KEY (product_code) REFERENCES products(code)
);

CREATE TABLE route_steps (
  bom_code TEXT NOT NULL,
  sequence INTEGER NOT NULL,
  machine_code TEXT NOT NULL,
  cycle_time_seconds REAL,
  min_batch_qty REAL,
  PRIMARY KEY (bom_code, sequence),
  FOREIGN KEY (bom_code) REFERENCES routes(bom_code),
  FOREIGN KEY (machine_code) REFERENCES machines(code)
);

CREATE TABLE parameters (
  product_code TEXT NOT NULL,
  bom_code TEXT NOT NULL,
  machine_code TEXT NOT NULL,
  sequence INTEGER NOT NULL,
  key TEXT NOT NULL,
  value REAL,
  value_text TEXT,
  unit TEXT,
  FOREIGN KEY (bom_code, sequence) REFERENCES route_steps(bom_code, sequence),
  FOREIGN KEY (machine_code) REFERENCES machines(code)
);

CREATE INDEX idx_routes_product ON routes(product_code);
CREATE INDEX idx_route_steps_machine ON route_steps(machine_code);
CREATE INDEX idx_params_bom ON parameters(bom_code);
CREATE INDEX idx_params_machine ON parameters(machine_code);
CREATE INDEX idx_params_key ON parameters(key);
"""

def main():
    if os.path.exists(DB):
        os.remove(DB)

    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)

    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)

    with con:
        con.executemany(
            "INSERT INTO machines (code, name, type) VALUES (?, ?, ?)",
            [(m["code"], m["name"], m.get("type")) for m in data["machines"]],
        )

        con.executemany(
            "INSERT INTO products (code, product_group) VALUES (?, ?)",
            [(p["code"], p.get("group")) for p in data["products"]],
        )

        route_rows = []
        step_rows = []
        for r in data["routes"]:
            route_rows.append((r["product_code"], r["bom_code"], r["version"]))
            for s in r.get("steps", []):
                step_rows.append((
                    r["bom_code"],
                    s["sequence"],
                    s["machine_code"],
                    s.get("cycle_time_seconds"),
                    s.get("min_batch_qty"),
                ))

        con.executemany(
            "INSERT INTO routes (product_code, bom_code, version) VALUES (?, ?, ?)",
            route_rows,
        )
        con.executemany(
            "INSERT INTO route_steps (bom_code, sequence, machine_code, cycle_time_seconds, min_batch_qty) VALUES (?, ?, ?, ?, ?)",
            step_rows,
        )

        param_rows = []
        for p in data["parameters"]:
            param_rows.append((
                p["product_code"],
                p["bom_code"],
                p["machine_code"],
                p["sequence"],
                p["key"],
                p.get("value"),
                p.get("value_text"),
                p.get("unit"),
            ))
        con.executemany(
            "INSERT INTO parameters (product_code, bom_code, machine_code, sequence, key, value, value_text, unit) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            param_rows,
        )

    counts = {
        tbl: con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        for tbl in ["machines", "products", "routes", "route_steps", "parameters"]
    }
    con.close()

    print("Row counts:")
    for tbl, n in counts.items():
        print(f"  {tbl}: {n}")

    assert counts["machines"] == 17, f"Expected 17 machines, got {counts['machines']}"
    assert counts["products"] == 50, f"Expected 50 products, got {counts['products']}"
    assert counts["routes"] == 626, f"Expected 626 routes, got {counts['routes']}"
    assert counts["parameters"] == 77469, f"Expected 77469 parameters, got {counts['parameters']}"
    print("All counts verified.")
    print(f"Database written to: {os.path.abspath(DB)}")

if __name__ == "__main__":
    main()
