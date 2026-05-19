# Analisi Prestazioni Query - DB Malattie Infettive

- Data test: 2026-03-31T11:42:04
- Database: `gesan_malattieinfettive` @ `10.10.13.11:5432`
- Metodo: query reali con `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`; DML in transazione con `ROLLBACK`.

## 1) Top 4 tabelle più gravose

| Tabella | Total size | Table data | Indexes | Row estimate | Row count (exact) |
|---|---:|---:|---:|---:|---:|
| `gesan_malattie_infettive_ie_modelli` | 13.00 MB | 0.01 MB | 0.03 MB | 22 | 22 |
| `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen` | 2.42 MB | 1.88 MB | 0.51 MB | 8,374 | 8,374 |
| `gesan_malattie_infettive_segnalazione` | 1.98 MB | 1.73 MB | 0.21 MB | 2,974 | 2,974 |
| `gesan_malattie_infettive_ie` | 1.26 MB | 1.05 MB | 0.12 MB | 1,281 | 1,281 |

## 2) Indici delle 4 tabelle

### `gesan_malattie_infettive_ie_modelli`
| Index | Size | Unique | Primary |
|---|---:|:---:|:---:|
| `unique_gesan_malattie_infettive_ie_modelli_nome_indagine` | 0.02 MB | Y | N |
| `gesan_malattie_infettive_ie_modelli_pkey` | 0.02 MB | Y | Y |

- `unique_gesan_malattie_infettive_ie_modelli_nome_indagine`: `CREATE UNIQUE INDEX unique_gesan_malattie_infettive_ie_modelli_nome_indagine ON gesan_malattie_infettive_ie_modelli USING btree (nome_indagine)`
- `gesan_malattie_infettive_ie_modelli_pkey`: `CREATE UNIQUE INDEX gesan_malattie_infettive_ie_modelli_pkey ON gesan_malattie_infettive_ie_modelli USING btree (id)`

### `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen`
| Index | Size | Unique | Primary |
|---|---:|:---:|:---:|
| `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_a_pkey` | 0.51 MB | Y | Y |

- `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_a_pkey`: `CREATE UNIQUE INDEX gesan_malattie_infettive_ie_infezioni_alimentari_consumo_a_pkey ON gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen USING btree (id)`

### `gesan_malattie_infettive_segnalazione`
| Index | Size | Unique | Primary |
|---|---:|:---:|:---:|
| `gesan_malattie_infettive_segnalazione_pkey` | 0.21 MB | Y | Y |

- `gesan_malattie_infettive_segnalazione_pkey`: `CREATE UNIQUE INDEX gesan_malattie_infettive_segnalazione_pkey ON gesan_malattie_infettive_segnalazione USING btree (id)`

### `gesan_malattie_infettive_ie`
| Index | Size | Unique | Primary |
|---|---:|:---:|:---:|
| `gesan_malattie_infettive_indagine_epidemiologica_pkey` | 0.12 MB | Y | Y |

- `gesan_malattie_infettive_indagine_epidemiologica_pkey`: `CREATE UNIQUE INDEX gesan_malattie_infettive_indagine_epidemiologica_pkey ON gesan_malattie_infettive_ie USING btree (id)`

## 3) Benchmark DML (INSERT/UPDATE/DELETE)

| Tabella | Test | Exec ms | Plan ms | Buffers (hit/read) | Esito |
|---|---|---:|---:|---|---|
| `gesan_malattie_infettive_ie_modelli` | INSERT 1 | 15.972 | - | 580/98 | OK |
| `gesan_malattie_infettive_ie_modelli` | INSERT 10 | 243.759 | - | 6290/427 | OK |
| `gesan_malattie_infettive_ie_modelli` | INSERT 100 | 2076.425 | - | 62983/4165 | OK |
| `gesan_malattie_infettive_ie_modelli` | UPDATE 1 | 143.253 | - | 9/0 | OK |
| `gesan_malattie_infettive_ie_modelli` | UPDATE 10 | 0.349 | - | 15/1 | OK |
| `gesan_malattie_infettive_ie_modelli` | UPDATE 100 | 0.271 | - | 26/0 | OK |
| `gesan_malattie_infettive_ie_modelli` | DELETE 1 | 2.087 | - | 253/1 | OK |
| `gesan_malattie_infettive_ie_modelli` | DELETE 10 | 88.819 | - | 4433/846 | OK |
| `gesan_malattie_infettive_ie_modelli` | DELETE 100 | 317.143 | - | 7730/657 | OK |
| `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen` | INSERT 1 | 0.391 | - | 0/7 | OK |
| `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen` | INSERT 10 | 0.900 | - | 40/3 | OK |
| `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen` | INSERT 100 | 6.359 | - | 406/5 | OK |
| `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen` | UPDATE 1 | 8.394 | - | 15/236 | OK |
| `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen` | UPDATE 10 | 26.953 | - | 296/10 | OK |
| `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen` | UPDATE 100 | 33.169 | - | 817/41 | OK |
| `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen` | DELETE 1 | 3.196 | - | 249/0 | OK |
| `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen` | DELETE 10 | 4.355 | - | 258/0 | OK |
| `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen` | DELETE 100 | 5.805 | - | 350/0 | OK |
| `gesan_malattie_infettive_segnalazione` | INSERT 1 | 2.808 | - | 1/8 | OK |
| `gesan_malattie_infettive_segnalazione` | INSERT 10 | 3.798 | - | 36/2 | OK |
| `gesan_malattie_infettive_segnalazione` | INSERT 100 | 23.905 | - | 352/22 | OK |
| `gesan_malattie_infettive_segnalazione` | UPDATE 1 | 8.036 | - | 82/221 | OK |
| `gesan_malattie_infettive_segnalazione` | UPDATE 10 | 21.201 | - | 302/10 | OK |
| `gesan_malattie_infettive_segnalazione` | UPDATE 100 | 31.956 | - | 919/18 | OK |
| `gesan_malattie_infettive_segnalazione` | DELETE 1 | 8.982 | - | 254/0 | OK |
| `gesan_malattie_infettive_segnalazione` | DELETE 10 | 21.092 | - | 272/0 | OK |
| `gesan_malattie_infettive_segnalazione` | DELETE 100 | 149.589 | - | 459/0 | OK |
| `gesan_malattie_infettive_ie` | INSERT 1 | 0.717 | - | 0/7 | OK |
| `gesan_malattie_infettive_ie` | INSERT 10 | 1.405 | - | 34/7 | OK |
| `gesan_malattie_infettive_ie` | INSERT 100 | 8.669 | - | 405/14 | OK |
| `gesan_malattie_infettive_ie` | UPDATE 1 | 2.563 | - | 39/117 | OK |
| `gesan_malattie_infettive_ie` | UPDATE 10 | 9.160 | - | 207/6 | OK |
| `gesan_malattie_infettive_ie` | UPDATE 100 | 14.470 | - | 870/13 | OK |
| `gesan_malattie_infettive_ie` | DELETE 1 | 2.101 | - | 151/0 | OK |
| `gesan_malattie_infettive_ie` | DELETE 10 | 5.521 | - | 169/0 | OK |
| `gesan_malattie_infettive_ie` | DELETE 100 | 40.494 | - | 357/0 | OK |

## 4) SELECT * + EXPLAIN (ANALYZE, BUFFERS)

| Tabella | Exec ms | Plan ms | Top node | Actual rows | Buffers (hit/read) |
|---|---:|---:|---|---:|---|
| `gesan_malattie_infettive_ie_modelli` | 0.029 | - | Seq Scan | 22 | 2/0 |
| `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen` | 2.726 | - | Seq Scan | 8,374 | 247/0 |
| `gesan_malattie_infettive_segnalazione` | 0.865 | - | Seq Scan | 2,974 | 251/0 |
| `gesan_malattie_infettive_ie` | 0.513 | - | Seq Scan | 1,281 | 148/0 |

## 5) Join query usate (con EXPLAIN ANALYZE)

| Join query | Exec ms | Plan ms | Top node | Actual rows |
|---|---:|---:|---|---:|
| Influenza+Segnalazione | 2.214 | - | Limit | 100 |
| Legionellosi+Segnalazione | 2.134 | - | Limit | 100 |
| EpatiteA+Segnalazione | 0.697 | - | Limit | 29 |

## 6) Note metodologiche
- DML eseguite in transazione con rollback: nessuna modifica persistente al DB.
- Per INSERT i valori sono derivati da una riga esistente, modificando PK/colonne univoche per evitare collisioni.
- Se il server PostgreSQL non espone Planning Time in JSON, il campo appare come `-`.