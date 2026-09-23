# Auditoría de trazabilidad end-to-end — Misión 10

**Proyecto:** Dietas al Día · **Épica:** EPC28 — Asignación de tratamiento nutricional
**Curso:** Ingeniería de Requisitos (UPB) · **Auditor:** Mateo Roldán
**Fecha de auditoría:** 2026-09-23 · **Alcance:** cadena completa necesidad de negocio → requisito → código → prueba → resultado

---

## 1. Objetivo

Verificar que los requisitos derivados de la épica EPC28 completaron correctamente su ciclo de vida y que existe trazabilidad consistente entre la necesidad de negocio, los requisitos funcionales (RF1–RF7), el código del prototipo, los casos de prueba y sus resultados — identificando cualquier ruptura en la cadena antes de dar por cerrada la épica.

## 2. Metodología

Esta auditoría **no se hizo leyendo documentos sueltos y armando la matriz a mano**: se generó ejecutando `tools/build_matrix.py`, que lee directamente:

1. **El código del prototipo** (`dietas-al-dia-prototipo.html`), a través del bloque `<script type="application/json" id="trace-data">` embebido en el propio archivo, que declara qué función implementa cada RF y qué CA cubre.
2. **README.md**, del que extrae las tablas de pruebas de aceptación (sección 4) y de defectos (sección 5).
3. **`artifacts/registry.yaml`**, el catálogo de metadatos de ciclo de vida de cada artefacto (Misión 9).

El resultado es `docs/matriz_trazabilidad_dietas_al_dia.xlsx`. Esto significa que la matriz y esta auditoría se pueden **regenerar en cualquier momento** con un solo comando y siempre van a reflejar el estado real del código, no una foto desactualizada:

```bash
pip install openpyxl pyyaml
python tools/build_matrix.py
```

## 3. Trazabilidad end-to-end por requisito

| Necesidad | Requisito | CA | Código | Prueba | Estado final |
|---|---|---|---|---|---|
| EPC28 | RF1 — Listar dietas por diagnóstico | CA1 | `selP()`, `render()` | Inspección manual | Verificado |
| EPC28 | RF2 — Marcar dietas con alérgeno/incompatibilidad | CA2 | `cf()`, `alerts()`, `render()` | Inspección manual | Verificado |
| EPC28 | RF3 — Confirmación explícita ante alerta | CA2 | `asignar()`, `okM()`, `closeM()` | Inspección manual | Verificado |
| EPC28 | RF4 — Ficha técnica con paciente siempre visible | CA3 | `ver()`, `render()` | Inspección manual | Verificado |
| EPC28 | RF5 — Dietas seguras primero, decisión < 90 s | CA4 | `render()`, `startT()`, `fin()`, `renderT()` | TC-CA4 (P1–P5) | **Verificado con reserva** (4/5, 80 %) |
| EPC28 | RF6 — Registrar dieta asignada | Soporte de la épica | `fin()` | — | **Implementado (parcial)** |
| EPC28 | RF7 — Buscar paciente por nombre/cédula | Soporte | — | — | **No implementado** |

(Tabla generada a partir de la misma fuente que `docs/matriz_trazabilidad_dietas_al_dia.xlsx`; ver esa hoja `📋 Matriz principal` para el detalle completo con responsables y fechas.)

## 4. Rupturas de trazabilidad detectadas

### 4.1 RF7 — sin código ni prueba (ruptura completa)
El README y la épica original mencionan RF7 ("buscar pacientes por nombre o número de seguridad social", prioridad Baja), pero el prototipo **no tiene ningún campo de búsqueda**: solo ofrece un `<select>` con los 3 pacientes precargados (`P` en el código). No hay función, ni caso de prueba, ni defecto que lo cubra.

- **Impacto:** bajo (requisito de soporte, prioridad Baja, no bloquea la validación de la épica).
- **Causa raíz:** se priorizó implementar y probar CA1–CA4 (los criterios que sí definen la épica) antes que un requisito de soporte.
- **Recomendación:** diferir formalmente RF7 a una siguiente iteración del prototipo (o abrir una RFC si el Departamento de Nutrición lo requiere antes), dejando constancia explícita en `artifacts/registry.yaml` (ya registrado como `estado_final: No implementado`) en vez de dejarlo como una omisión silenciosa.

### 4.2 RF6 — implementado sin caso de prueba y sin persistencia real
`fin()` sí registra la dieta asignada (`S.asg[p.id]`), pero:
- No existe un caso de prueba dedicado que lo verifique de forma independiente (solo se ejercita como efecto secundario de asignar una dieta).
- La "persistencia" vive en una variable de JavaScript en memoria del navegador: se pierde al recargar la página. No hay backend ni base de datos (documentado como DEF-03: no guarda fecha ni médico que confirmó la alerta).

- **Impacto:** medio — es parte de la épica (registrar el tratamiento asignado), no un requisito periférico como RF7.
- **Recomendación:** antes de pasar el prototipo a desarrollo real, escribir un caso de prueba explícito para RF6 y definir el modelo de persistencia (encaja con DEF-03).

### 4.3 RF5 — verificado con reserva, no cierre definitivo
La prueba de aceptación con usuarios (sección 4 de README.md) dio 4/5 (80 %): el participante P4 tardó 97 s por un problema de jerarquía visual (DEF-05), no por un fallo de seguridad clínica. El propio README (sección 7) ya condiciona el cierre de CA4 a corregir DEF-05 y DEF-06 y repetir la prueba con un participante adicional.

- **Impacto:** medio — no compromete la seguridad clínica (ningún participante recibió una dieta insegura sin confirmar), pero el criterio cuantitativo de CA4 (90 s) no se cumplió al 100 %.
- **Recomendación:** no cerrar RF5/CA4 como "Verificado" pleno hasta repetir la prueba tras corregir DEF-05 y DEF-06. Se deja registrado como `Verificado con reserva` en `artifacts/registry.yaml`, no como `Verificado`, precisamente para que esta ruptura sea visible y no se pierda al archivar el proyecto.

### 4.4 Consistencia terminológica (heredada de la validación previa)
La auditoría IEEE original (README.md sección 3) ya había detectado que la historia de usuario usaba "alergias" mientras que los CA usaban "alérgeno/incompatible". Esto se resolvió con **RFC-001** (reformulación de CA1–CA4, unificando el término "alérgeno/incompatibilidad"). Se verifica que RFC-001 quedó registrada con sus requisitos afectados (RF1–RF5) en `artifacts/registry.yaml` y en la hoja "Registro de RFCs" de la matriz — la cadena de cambio quedó documentada, no se perdió trazabilidad al reformular.

## 5. Verificación de cierre de la épica EPC28

| Criterio de cierre | Resultado |
|---|---|
| Todos los RF tienen un requisito de origen (EPC28) | ✅ Sí — 7/7 |
| Todos los RF tienen código asociado | ⚠ Parcial — 6/7 (RF7 no implementado) |
| Todos los RF tienen al menos un caso de prueba | ⚠ Parcial — 5/7 (RF6 y RF7 sin prueba) |
| Los defectos abiertos están vinculados a un RF | ✅ Sí — DEF-01 a DEF-06 todos referencian un RF en `artifacts/registry.yaml` |
| Los cambios a los CA quedaron registrados como RFC | ✅ Sí — RFC-001 |
| Metadatos mínimos (ID, versión, estado, autor/revisor, fecha de cierre, artefactos relacionados) en cada artefacto | ✅ Sí — ver `artifacts/registry.yaml` |

**Conclusión de la auditoría:** la épica EPC28 puede considerarse **validada de forma condicional**, consistente con la decisión ya documentada en README.md sección 7. No se encontraron rupturas que invaliden la funcionalidad de seguridad clínica (RF1–RF4 verificados sin reservas), pero el cierre definitivo del ciclo de vida de la épica queda sujeto a tres acciones pendientes:

1. Repetir la prueba CA4 con un participante adicional tras corregir DEF-05 y DEF-06 (cierra RF5 sin reserva).
2. Definir y probar la persistencia real de la dieta asignada (cierra RF6).
3. Decidir formalmente si RF7 se implementa en la siguiente iteración o se archiva fuera de alcance (cierra RF7 con un estado explícito en vez de dejarlo abierto indefinidamente).

Hasta que esas tres acciones se resuelvan, el estado de la épica en `artifacts/registry.yaml` se mantiene como `Validada condicionalmente`, no `Cerrada`.
