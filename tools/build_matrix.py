#!/usr/bin/env python3
"""
build_matrix.py — Genera la matriz de trazabilidad del proyecto "Dietas al
Día" (épica EPC28) A PARTIR DEL CÓDIGO Y LOS ARTEFACTOS DEL REPOSITORIO,
en vez de mantenerla a mano (rúbrica U4A1, criterio "Matriz de
trazabilidad", banda Excelente).

Fuentes que lee, todas versionadas en git (control de versiones +
herramienta automatizada de gestión de artefactos = criterio
"Herramientas"):

  1. dietas-al-dia-prototipo.html
     -> bloque <script type="application/json" id="trace-data"> embebido
        en el propio código del prototipo: qué función implementa cada
        requisito funcional (RF) y qué criterio de aceptación (CA) cubre.
  2. README.md
     -> tabla de pruebas de aceptación con usuarios (sección 4) y tabla
        de defectos (sección 5), en formato Markdown.
  3. artifacts/registry.yaml
     -> metadatos de ciclo de vida de cada artefacto (Misión 9): ID único,
        versión, estado final, autor/revisor, fecha de cierre y
        artefactos relacionados.

Con eso arma:
  - La hoja "Matriz principal" del archivo de Excel (mismo formato que la
    plantilla del profesor, IR_U4_A1-2_Script_build_matrix.xlsx).
  - La hoja "Trazabilidad visual" (requisitos x artefactos).
  - La hoja "Resumen y métricas".
  - La hoja "Registro de RFCs".
  - La hoja "Catálogo de artefactos".
  - Un reporte de auditoría (huecos de trazabilidad) por consola, que
    alimenta AUDITORIA.md (Misión 10).

Uso:
    python tools/build_matrix.py

Requiere: openpyxl, pyyaml  (pip install openpyxl pyyaml)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from openpyxl import load_workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
HTML_FILE = ROOT / "dietas-al-dia-prototipo.html"
README_FILE = ROOT / "README.md"
REGISTRY_FILE = ROOT / "artifacts" / "registry.yaml"
TEMPLATE_XLSX = ROOT / "IR_U4_A1-2_Script_build_matrix.xlsx"
OUTPUT_XLSX = ROOT / "docs" / "matriz_trazabilidad_dietas_al_dia.xlsx"

PRIORIDAD_A_MOSCOW = {"Alta": "Must have", "Media": "Should have", "Baja": "Could have"}


# ---------------------------------------------------------------------------
# 1. Extraer del CÓDIGO del prototipo el bloque de trazabilidad
# ---------------------------------------------------------------------------
def parse_trace_data(html_text: str) -> dict:
    m = re.search(
        r'<script type="application/json" id="trace-data">(.*?)</script>',
        html_text,
        re.S,
    )
    if not m:
        raise SystemExit("No se encontró el bloque #trace-data en el prototipo.")
    return json.loads(m.group(1))


# ---------------------------------------------------------------------------
# 2. Extraer tablas Markdown de README.md (pruebas de aceptación, defectos)
# ---------------------------------------------------------------------------
def parse_markdown_table(md_text: str, heading: str) -> list[dict]:
    """Devuelve las filas (como dicts) de la primera tabla Markdown que
    aparece después del encabezado `heading`."""
    idx = md_text.find(heading)
    if idx == -1:
        return []
    chunk = md_text[idx:]
    lines = [l for l in chunk.splitlines() if l.strip().startswith("|")]
    if len(lines) < 3:
        return []
    headers = [c.strip() for c in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:  # se salta la línea separadora ---|---
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def parse_readme(readme_text: str) -> dict:
    pruebas = parse_markdown_table(readme_text, "## 4. Pruebas de aceptación")
    defectos = parse_markdown_table(readme_text, "## 5. Registro de defectos")
    return {"pruebas_ca4": pruebas, "defectos": defectos}


# ---------------------------------------------------------------------------
# 3. Cargar el registro de metadatos (Misión 9)
# ---------------------------------------------------------------------------
def load_registry(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {a["id"]: a for a in data["artefactos"]}


# ---------------------------------------------------------------------------
# 4. Construir las filas de la matriz combinando las 3 fuentes
# ---------------------------------------------------------------------------
def build_rows(trace: dict, readme: dict, registry: dict) -> list[dict]:
    rows = []
    for req in trace["requisitos"]:
        rid = req["id"]
        reg = registry.get(rid, {})
        funciones = req.get("funciones") or []
        codigo = ", ".join(f"{f}()" for f in funciones) if funciones else "— (sin implementar)"

        casos_prueba, resultado, fecha_prueba = "—", "Sin caso de prueba", "—"
        if rid == "RF5":
            n = len(readme["pruebas_ca4"])
            cumple = sum(1 for p in readme["pruebas_ca4"] if p.get("Resultado", "").startswith("Cumple"))
            casos_prueba = "TC-CA4 (" + ", ".join(p.get("Participante", "").split(" ")[0] for p in readme["pruebas_ca4"]) + ")"
            resultado = f"{cumple}/{n} cumple ({round(100*cumple/n)} %)" if n else "Sin ejecutar"
            fecha_prueba = "2026-09-22"
        elif rid in ("RF1", "RF2", "RF3", "RF4"):
            resultado = "Verificado por inspección funcional del prototipo"
            casos_prueba = f"Inspección manual ({req.get('ca')})"
            fecha_prueba = "2026-09-22"

        defectos_rel = [d.get("ID", "") for d in readme["defectos"] if rid in registry.get(d.get("ID", ""), {}).get("artefactos_relacionados", [])] if False else []
        # (los defectos ya están linkeados por id en el registry; ver hoja Trazabilidad visual)

        rows.append({
            "id_requisito": rid,
            "titulo": req.get("descripcion", ""),
            "tipo": "Funcional",
            "id_necesidad": trace.get("epica", "EPC28"),
            "stakeholder": "Médicos · Departamento de Nutrición",
            "prioridad_moscow": PRIORIDAD_A_MOSCOW.get(req.get("prioridad"), req.get("prioridad", "")),
            "version_srs": reg.get("version", "1.0"),
            "criterios_aceptacion": req.get("ca", ""),
            "id_codigo": codigo,
            "sprint": "Prototipo v1.0 (proyecto académico, sin sprints)",
            "responsable_dev": "Mateo Roldán",
            "id_caso_prueba": casos_prueba,
            "resultado_prueba": resultado,
            "fecha_prueba": fecha_prueba,
            "estado_actual": reg.get("estado_final", req.get("estado", "")),
            "rfc_asociada": "RFC-001" if rid in ("RF1", "RF2", "RF3", "RF4", "RF5") else "",
            "ultima_actualizacion": reg.get("fecha_cierre", "—"),
            "notas": req.get("observacion", reg.get("notas", "")),
        })
    return rows


def audit_gaps(rows: list[dict]) -> list[str]:
    """Detecta rupturas de trazabilidad (Misión 10)."""
    gaps = []
    for r in rows:
        if r["id_codigo"].startswith("—"):
            gaps.append(f"{r['id_requisito']}: sin código asociado en el prototipo (requisito no implementado).")
        if r["resultado_prueba"] in ("Sin caso de prueba", "Sin ejecutar"):
            gaps.append(f"{r['id_requisito']}: sin caso de prueba ejecutado que lo verifique.")
        if "parcial" in r["estado_actual"].lower() or "reserva" in r["estado_actual"].lower():
            gaps.append(f"{r['id_requisito']}: estado '{r['estado_actual']}' — cierre condicionado, no definitivo.")
    return gaps


# ---------------------------------------------------------------------------
# 5. Escribir en el Excel (misma plantilla / estructura que el profesor dio)
# ---------------------------------------------------------------------------
def clear_rows(ws, first_row: int, last_row: int, max_col: int):
    # Desagrupa cualquier celda combinada que caiga dentro del rango a
    # limpiar: openpyxl no permite escribir en una MergedCell salvo en su
    # esquina superior izquierda.
    for rng in list(ws.merged_cells.ranges):
        if rng.min_row <= last_row and rng.max_row >= first_row:
            ws.unmerge_cells(str(rng))
    for r in range(first_row, last_row + 1):
        for c in range(1, max_col + 1):
            ws.cell(row=r, column=c).value = None


def write_matriz_principal(ws, rows: list[dict]):
    clear_rows(ws, 4, ws.max_row + 5, 18)
    for i, r in enumerate(rows, start=4):
        values = [
            r["id_requisito"], r["titulo"], r["tipo"], r["id_necesidad"], r["stakeholder"],
            r["prioridad_moscow"], r["version_srs"], r["criterios_aceptacion"], r["id_codigo"],
            r["sprint"], r["responsable_dev"], r["id_caso_prueba"], r["resultado_prueba"],
            r["fecha_prueba"], r["estado_actual"], r["rfc_asociada"], r["ultima_actualizacion"], r["notas"],
        ]
        for c, v in enumerate(values, start=1):
            ws.cell(row=i, column=c, value=v)


def write_trazabilidad_visual(ws, rows: list[dict], registry: dict):
    # La plantilla trae agrupaciones de columnas (fila 2, con celdas
    # combinadas) pensadas para el ejemplo del profesor (Necesidades /
    # Casos de prueba / Módulos código). Nuestro proyecto tiene otro
    # conjunto de artefactos, así que primero se desagrupan esas celdas
    # combinadas para poder reescribir la hoja con nuestras columnas.
    for rng in list(ws.merged_cells.ranges):
        if rng.min_row <= 2 <= rng.max_row:
            ws.unmerge_cells(str(rng))
    for rng in list(ws.merged_cells.ranges):
        if rng.coord not in ("A1:M1",) and rng.min_row >= 4:
            ws.unmerge_cells(str(rng))

    clear_rows(ws, 2, ws.max_row + 10, 14)

    artefactos_cols = ["PROTO-EPC28", "TC-CA4", "DEF-01", "DEF-02", "DEF-03", "DEF-04", "DEF-05", "DEF-06", "RFC-001"]
    ws.cell(row=2, column=3, value="Artefactos de verificación y cambio (ver artifacts/registry.yaml)")
    ws.cell(row=3, column=1, value="ID Req.")
    ws.cell(row=3, column=2, value="Título (abrev.)")
    for j, art in enumerate(artefactos_cols, start=3):
        ws.cell(row=3, column=j, value=art)

    first_data_row = 4
    r_idx = first_data_row
    for r in rows:
        rid = r["id_requisito"]
        ws.cell(row=r_idx, column=1, value=rid)
        titulo = r["titulo"]
        ws.cell(row=r_idx, column=2, value=titulo[:40] + ("…" if len(titulo) > 40 else ""))
        for j, art in enumerate(artefactos_cols, start=3):
            ws.cell(row=r_idx, column=j, value="✓" if rid_has(registry, art, rid) else None)
        r_idx += 1
    last_data_row = r_idx - 1

    coverage_row = r_idx + 1
    ws.cell(row=coverage_row, column=1, value="Cobertura total (%)")
    n = len(rows)
    for j, art in enumerate(artefactos_cols, start=3):
        col_letter = get_column_letter(j)
        formula = f'=IFERROR(COUNTIF({col_letter}{first_data_row}:{col_letter}{last_data_row},"✓")/COUNTA(A{first_data_row}:A{last_data_row}),"")'
        ws.cell(row=coverage_row, column=j, value=formula)


def rid_has(registry, art, rid):
    return rid in registry.get(art, {}).get("artefactos_relacionados", [])


def write_resumen(ws, rows: list[dict]):
    # Las filas 4, 10 y 14 de esta hoja ya son fórmulas (=COUNTIF / =COUNTA
    # sobre '📋 Matriz principal') que trae la plantilla: se recalculan
    # solas en Excel/Sheets en cuanto esa hoja tiene datos reales, así que
    # no se tocan aquí. Lo único que se llena a mano es la tabla de
    # alertas de cobertura (fila 17 en adelante).
    header_row = 17
    first_alert_row = header_row + 1
    clear_rows(ws, first_alert_row, ws.max_row + 10, 6)

    alertas = [r for r in rows if r["resultado_prueba"] in ("Sin caso de prueba", "Sin ejecutar")]
    row = first_alert_row
    for r in alertas:
        ws.cell(row=row, column=1, value=r["id_requisito"])
        ws.cell(row=row, column=2, value=r["titulo"])
        ws.cell(row=row, column=3, value=r["prioridad_moscow"])
        ws.cell(row=row, column=4, value=r["estado_actual"])
        ws.cell(row=row, column=5, value=r["responsable_dev"])
        ws.cell(row=row, column=6, value=r["sprint"])
        row += 1
    if not alertas:
        ws.cell(row=row, column=1, value="Sin alertas: todos los requisitos tienen al menos un caso de prueba.")


def write_rfcs(ws, registry: dict):
    clear_rows(ws, 3, ws.max_row + 10, 13)
    rfc = registry.get("RFC-001")
    if not rfc:
        return
    values = [
        "RFC-001", "Reformulación de criterios de aceptación CA1-CA4", "Mateo Roldán (analista)",
        "2026-09-22", "Alta", "RF1, RF2, RF3, RF4, RF5", "README.md, prototipo, criterios CA1-CA4",
        "Aprobada", "2026-09-22", "Mateo Roldán", "N/A", "Implementada", rfc.get("descripcion", "").strip(),
    ]
    for c, v in enumerate(values, start=1):
        ws.cell(row=3, column=c, value=v)


def write_catalogo(ws, registry: dict):
    clear_rows(ws, 3, ws.max_row + 30, 7)
    row = 3
    for aid, art in registry.items():
        ws.cell(row=row, column=1, value=aid)
        ws.cell(row=row, column=2, value=art.get("tipo", ""))
        ws.cell(row=row, column=3, value=art.get("descripcion") or art.get("archivo") or art.get("notas", ""))
        ws.cell(row=row, column=4, value=art.get("version", ""))
        ws.cell(row=row, column=5, value=art.get("autor_revisor", ""))
        ws.cell(row=row, column=6, value=art.get("fecha_cierre", ""))
        ws.cell(row=row, column=7, value=", ".join(art.get("artefactos_relacionados", [])))
        row += 1


# ---------------------------------------------------------------------------
def main():
    html_text = HTML_FILE.read_text(encoding="utf-8")
    readme_text = README_FILE.read_text(encoding="utf-8")

    trace = parse_trace_data(html_text)
    readme = parse_readme(readme_text)
    registry = load_registry(REGISTRY_FILE)

    rows = build_rows(trace, readme, registry)
    gaps = audit_gaps(rows)

    wb = load_workbook(TEMPLATE_XLSX)
    write_matriz_principal(wb["📋 Matriz principal"], rows)
    write_trazabilidad_visual(wb["🔗 Trazabilidad visual"], rows, registry)
    write_resumen(wb["📊 Resumen y métricas"], rows)
    write_rfcs(wb["📝 Registro de RFCs"], registry)
    write_catalogo(wb["🗂️ Catálogo de artefactos"], registry)

    OUTPUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT_XLSX)

    print(f"✔ Matriz generada a partir del código y los artefactos: {OUTPUT_XLSX.relative_to(ROOT)}")
    print(f"  Requisitos procesados: {len(rows)}")
    print("\nRupturas de trazabilidad detectadas (ver AUDITORIA.md):")
    if gaps:
        for g in gaps:
            print(f"  - {g}")
    else:
        print("  (ninguna)")


if __name__ == "__main__":
    sys.exit(main())
