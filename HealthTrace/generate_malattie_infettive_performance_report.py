#!/usr/bin/env python3
"""
Generate performance report for infectious-disease database.

Output:
  HealthTrace/MALATTIE_INFETTIVE_QUERY_PERFORMANCE_REPORT.md
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor


def fmt_mb(value: Any) -> str:
    return f"{(value or 0) / 1024 / 1024:.2f} MB"


def fmt_ms(value: Any) -> str:
    return f"{value:.3f}" if isinstance(value, (int, float)) else "-"


def explain_json(cur: RealDictCursor, sql: str) -> tuple[dict[str, Any], float | None, float | None]:
    cur.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql)
    doc = cur.fetchone()["QUERY PLAN"][0]
    exec_ms = doc.get("Execution Time", doc.get("Total Runtime"))
    plan_ms = doc.get("Planning Time")
    return (
        doc,
        float(exec_ms) if exec_ms is not None else None,
        float(plan_ms) if plan_ms is not None else None,
    )


def get_single_pk(cur: RealDictCursor, table: str) -> str | None:
    cur.execute(
        """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = 'public'
          AND tc.table_name = %s
          AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY kcu.ordinal_position
        """,
        (table,),
    )
    rows = cur.fetchall()
    if len(rows) == 1:
        return rows[0]["column_name"]
    return None


def get_unique_single_cols(cur: RealDictCursor, table: str) -> set[str]:
    cur.execute(
        """
        SELECT a.attname AS col
        FROM pg_class t
        JOIN pg_namespace n ON n.oid = t.relnamespace
        JOIN pg_index i ON i.indrelid = t.oid
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = i.indkey[0]
        WHERE n.nspname = 'public'
          AND t.relname = %s
          AND i.indisunique = true
          AND i.indnatts = 1
        """,
        (table,),
    )
    return {r["col"] for r in cur.fetchall()}


def build_insert_sql(cur: RealDictCursor, table: str, batch: int) -> str:
    pk_col = get_single_pk(cur, table)
    unique_cols = get_unique_single_cols(cur, table)

    cur.execute(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
        """,
        (table,),
    )
    cols = cur.fetchall()

    targets: list[str] = []
    exprs: list[str] = []

    for col in cols:
        name = col["column_name"]
        data_type = col["data_type"]
        targets.append(name)

        if pk_col and name == pk_col and data_type in ("smallint", "integer", "bigint"):
            exprs.append(f'(SELECT COALESCE(MAX("{pk_col}"), 0) FROM "{table}") + g.i')
        elif name in unique_cols and data_type in ("character varying", "character", "text"):
            exprs.append(f'COALESCE(s."{name}", \'\') || \'_bench_\' || g.i')
        elif name in unique_cols and data_type in ("smallint", "integer", "bigint"):
            exprs.append(f'COALESCE(s."{name}", 0) + 1000000 + g.i')
        else:
            exprs.append(f's."{name}"')

    cols_sql = ", ".join(f'"{c}"' for c in targets)
    expr_sql = ", ".join(exprs)
    return (
        f'WITH g AS (SELECT generate_series(1,{batch}) i), '
        f'src AS (SELECT * FROM "{table}" LIMIT 1) '
        f'INSERT INTO "{table}" ({cols_sql}) '
        f"SELECT {expr_sql} FROM src s CROSS JOIN g"
    )


def run(args: argparse.Namespace) -> Path:
    conn = psycopg2.connect(
        host=args.host,
        port=args.port,
        dbname=args.dbname,
        user=args.user,
        password=args.password,
        connect_timeout=10,
    )
    conn.autocommit = False
    cur = conn.cursor(cursor_factory=RealDictCursor)

    report: list[str] = [
        "# Analisi Prestazioni Query - DB Malattie Infettive",
        "",
        f"- Data test: {datetime.now().isoformat(timespec='seconds')}",
        f"- Database: `{args.dbname}` @ `{args.host}:{args.port}`",
        "- Metodo: query reali con `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`; DML in transazione con `ROLLBACK`.",
        "",
    ]

    cur.execute(
        """
        SELECT c.relname AS table_name,
               pg_total_relation_size(c.oid) AS total_bytes,
               pg_relation_size(c.oid) AS table_bytes,
               pg_indexes_size(c.oid) AS index_bytes,
               c.reltuples::bigint AS est_rows
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'r'
          AND n.nspname = 'public'
          AND c.relname LIKE %s
        ORDER BY pg_total_relation_size(c.oid) DESC
        LIMIT 4
        """,
        (args.table_pattern,),
    )
    heavy = cur.fetchall()
    if not heavy:
        raise RuntimeError("No target tables found.")

    report += [
        "## 1) Top 4 tabelle più gravose",
        "",
        "| Tabella | Total size | Table data | Indexes | Row estimate | Row count (exact) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in heavy:
        table = row["table_name"]
        cur.execute(f'SELECT COUNT(*) AS cnt FROM "{table}"')
        cnt = cur.fetchone()["cnt"]
        report.append(
            f"| `{table}` | {fmt_mb(row['total_bytes'])} | {fmt_mb(row['table_bytes'])} | "
            f"{fmt_mb(row['index_bytes'])} | {int(row['est_rows'] or 0):,} | {int(cnt):,} |"
        )

    report += ["", "## 2) Indici delle 4 tabelle", ""]
    for row in heavy:
        table = row["table_name"]
        report += [f"### `{table}`", "| Index | Size | Unique | Primary |", "|---|---:|:---:|:---:|"]
        cur.execute(
            """
            SELECT i.relname AS index_name,
                   pg_relation_size(i.oid) AS index_bytes,
                   idx.indisunique AS is_unique,
                   idx.indisprimary AS is_primary,
                   pg_get_indexdef(i.oid) AS index_def
            FROM pg_class tbl
            JOIN pg_index idx ON tbl.oid = idx.indrelid
            JOIN pg_class i ON i.oid = idx.indexrelid
            JOIN pg_namespace n ON n.oid = tbl.relnamespace
            WHERE n.nspname = 'public' AND tbl.relname = %s
            ORDER BY pg_relation_size(i.oid) DESC
            """,
            (table,),
        )
        idxs = cur.fetchall()
        for idx in idxs:
            report.append(
                f"| `{idx['index_name']}` | {fmt_mb(idx['index_bytes'])} | "
                f"{'Y' if idx['is_unique'] else 'N'} | {'Y' if idx['is_primary'] else 'N'} |"
            )
        report.append("")
        for idx in idxs[:6]:
            report.append(f"- `{idx['index_name']}`: `{idx['index_def']}`")
        report.append("")

    report += [
        "## 3) Benchmark DML (INSERT/UPDATE/DELETE)",
        "",
        "| Tabella | Test | Exec ms | Plan ms | Buffers (hit/read) | Esito |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in heavy:
        table = row["table_name"]
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
            LIMIT 1
            """,
            (table,),
        )
        col = cur.fetchone()["column_name"]

        tests: list[tuple[str, str]] = []
        for n in (1, 10, 100):
            tests.append((f"INSERT {n}", build_insert_sql(cur, table, n)))
        for n in (1, 10, 100):
            tests.append(
                (
                    f"UPDATE {n}",
                    f'WITH tgt AS (SELECT ctid FROM "{table}" LIMIT {n}) '
                    f'UPDATE "{table}" t SET "{col}" = t."{col}" FROM tgt WHERE t.ctid = tgt.ctid',
                )
            )
        for n in (1, 10, 100):
            tests.append(
                (
                    f"DELETE {n}",
                    f'WITH tgt AS (SELECT ctid FROM "{table}" LIMIT {n}) '
                    f'DELETE FROM "{table}" t USING tgt WHERE t.ctid = tgt.ctid',
                )
            )

        for name, sql in tests:
            try:
                cur.execute("BEGIN")
                plan, exec_ms, plan_ms = explain_json(cur, sql)
                cur.execute("ROLLBACK")
                p = plan.get("Plan", {})
                report.append(
                    f"| `{table}` | {name} | {fmt_ms(exec_ms)} | {fmt_ms(plan_ms)} | "
                    f"{p.get('Shared Hit Blocks', 0)}/{p.get('Shared Read Blocks', 0)} | OK |"
                )
            except Exception as exc:
                try:
                    cur.execute("ROLLBACK")
                except Exception:
                    pass
                report.append(
                    f"| `{table}` | {name} | - | - | - | ERRORE: {str(exc).replace('|', '/')[:80]} |"
                )

    report += [
        "",
        "## 4) SELECT * + EXPLAIN (ANALYZE, BUFFERS)",
        "",
        "| Tabella | Exec ms | Plan ms | Top node | Actual rows | Buffers (hit/read) |",
        "|---|---:|---:|---|---:|---|",
    ]
    for row in heavy:
        table = row["table_name"]
        plan, exec_ms, plan_ms = explain_json(cur, f'SELECT * FROM "{table}"')
        p = plan.get("Plan", {})
        report.append(
            f"| `{table}` | {fmt_ms(exec_ms)} | {fmt_ms(plan_ms)} | {p.get('Node Type', '-')} | "
            f"{int(p.get('Actual Rows', 0)):,} | {p.get('Shared Hit Blocks', 0)}/{p.get('Shared Read Blocks', 0)} |"
        )

    joins = [
        (
            "Influenza+Segnalazione",
            "SELECT i.id, s.malattia_segnalata, s.data_segnalazione, s.comune_residenza_codice_istat "
            "FROM gesan_malattie_infettive_ie_influenza i "
            "JOIN gesan_malattie_infettive_segnalazione s ON s.id = i.id "
            "ORDER BY s.data_segnalazione DESC LIMIT 100",
        ),
        (
            "Legionellosi+Segnalazione",
            "SELECT l.id, s.malattia_segnalata, s.data_segnalazione, s.comune_residenza_codice_istat "
            "FROM gesan_malattie_infettive_ie_legionellosi l "
            "JOIN gesan_malattie_infettive_segnalazione s ON s.id = l.id "
            "ORDER BY s.data_segnalazione DESC LIMIT 100",
        ),
        (
            "EpatiteA+Segnalazione",
            "SELECT h.id, s.malattia_segnalata, s.data_segnalazione, s.comune_residenza_codice_istat "
            "FROM gesan_malattie_infettive_ie_epatite_a h "
            "JOIN gesan_malattie_infettive_segnalazione s ON s.id = h.id "
            "ORDER BY s.data_segnalazione DESC LIMIT 100",
        ),
    ]
    report += [
        "",
        "## 5) Join query usate (con EXPLAIN ANALYZE)",
        "",
        "| Join query | Exec ms | Plan ms | Top node | Actual rows |",
        "|---|---:|---:|---|---:|",
    ]
    for name, sql in joins:
        plan, exec_ms, plan_ms = explain_json(cur, sql)
        p = plan.get("Plan", {})
        report.append(
            f"| {name} | {fmt_ms(exec_ms)} | {fmt_ms(plan_ms)} | {p.get('Node Type', '-')} | {int(p.get('Actual Rows', 0)):,} |"
        )

    report += [
        "",
        "## 6) Note metodologiche",
        "- DML eseguite in transazione con rollback: nessuna modifica persistente al DB.",
        "- Per INSERT i valori sono derivati da una riga esistente, modificando PK/colonne univoche per evitare collisioni.",
        "- Se il server PostgreSQL non espone Planning Time in JSON, il campo appare come `-`.",
    ]

    output = Path(args.output).resolve()
    output.write_text("\n".join(report), encoding="utf-8")

    conn.rollback()
    cur.close()
    conn.close()
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate malattie infettive DB performance report.")
    parser.add_argument("--host", default="10.10.13.11")
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--dbname", default="gesan_malattieinfettive")
    parser.add_argument("--user", default="postgres")
    parser.add_argument("--password", default="postgres")
    parser.add_argument("--table-pattern", default="gesan_malattie_infettive%")
    parser.add_argument(
        "--output",
        default="/home/amir/Documents/amir/Ambientale/HealthTrace/MALATTIE_INFETTIVE_QUERY_PERFORMANCE_REPORT.md",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    output_path = run(args)
    print(f"Report generated: {output_path}")
