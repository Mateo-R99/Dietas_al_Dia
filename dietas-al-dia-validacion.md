# Validación de la épica EPC 28: Asignación de tratamiento nutricional

**Curso:** Ingeniería de Requisitos · **Caso:** Dietas al Día · **Prototipo:** enlace del artefacto publicado

## 1. Objetivo del prototipo
Validar con médicos del Departamento de Nutrición que el cruce automático entre el diagnóstico, el catálogo de dietas y las alergias del paciente permite elegir un tratamiento seguro sin revisar manualmente la historia clínica.

## 2. Traducción de la épica a requisitos funcionales

| ID | Requisito funcional | Prioridad | Criterio |
|---|---|---|---|
| RF1 | Al seleccionar un paciente, el sistema muestra en una sola pantalla las dietas asociadas a su enfermedad registrada | Alta | CA1 |
| RF2 | El sistema cruza alergias e incompatibilidades del paciente con los alimentos de cada dieta y marca las dietas en conflicto, nombrando el alimento | Alta | CA2 |
| RF3 | El sistema exige confirmación explícita antes de asignar una dieta con alerta | Alta | CA2 |
| RF4 | El médico abre la ficha técnica completa de la dieta con la cabecera del paciente siempre visible | Alta | CA3 |
| RF5 | El sistema muestra primero las dietas seguras y guía a un usuario nuevo para decidir en menos de 90 s | Media | CA4 |
| RF6 | El sistema registra la dieta asignada en el tratamiento del paciente | Media | Épica |
| RF7 | El sistema permite buscar pacientes por nombre o número de seguridad social | Baja | Soporte |

**Viabilidad técnica.** Entidades: Paciente, Enfermedad, Dieta, Alimento y Alérgeno (tabla Dieta–Alimento). El cruce exige que cada alimento tenga sus alérgenos etiquetados y que las alergias del paciente se registren de forma estructurada. El prototipo lo implementa con datos simulados.

## 3. Lista de verificación IEEE (atributos de calidad de requisitos)

| Atributo | Resultado | Evidencia / observación |
|---|---|---|
| Correcto | Cumple | Responde a la necesidad del médico de evitar el cruce manual |
| No ambiguo | Parcial | «Único paso», «ficha completa» y «señalar de forma inequívoca» no están definidos |
| Completo | Parcial | No define el comportamiento si el paciente no tiene alergias o si ninguna dieta es segura |
| Consistente | Parcial | La historia usa «alergias» y CA2 usa «alérgeno/incompatible» |
| Priorizado | No cumple | Los criterios no traen prioridad; se asignó en la sección 2 |
| Verificable | Parcial | CA4 tiene métrica (90 s); «sin pasar por alto ninguna alerta» requiere definir cómo se mide |
| Modificable | Cumple | Los criterios son independientes entre sí |
| Trazable | Parcial | No tenían identificador de requisito ni de prueba; ver sección 6 |

## 4. Pruebas de aceptación con usuarios sin ayuda
**Tarea:** «Asigna una dieta segura a la paciente Laura Pérez». **Criterio de éxito (CA4):** dieta segura, menos de 90 s y ninguna alerta ignorada. El prototipo registra estos datos automáticamente en su tabla de pruebas.

| Participante | Tiempo (s) | Dieta elegida | ¿Ignoró alerta? | ¿Navegación lógica? | Resultado |
|---|---|---|---|---|---|
| P1 – Estudiante Ing. Software | 41 | Rica en hierro | No | Sí | Cumple |
| P2 – Estudiante Ing. Software | 68 | Vegetariana rica en hierro | No | Sí, con una duda inicial sobre a qué botón entrar | Cumple |
| P3 – Auxiliar administrativo (sin formación clínica) | 39 | Rica en hierro | No | Sí | Cumple |
| P4 – Estudiante de otra carrera | 97 | Rica en hierro | No | No, exploró primero la ficha técnica de una dieta que no iba a elegir | No cumple (excede 90 s) |
| P5 – Estudiante Ing. Software | 52 | Vegetariana rica en hierro | Sí, intentó confirmar sin marcar la casilla de revisión y el sistema se lo impidió | Sí | Cumple |

**Resumen:** 4 de 5 participantes (80 %) cumplieron CA4. Ninguno asignó una dieta insegura sin confirmación explícita: el único intento de omitir la alerta (P5) fue bloqueado por el sistema, lo que valida el diseño de RF3. El caso que no cumplió (P4) fue por tiempo, no por seguridad, y se debió a que revisó una ficha técnica antes de decidir en vez de comparar las etiquetas de la lista.

## 5. Registro de defectos (Misión 7)
Hallazgos de la revisión del prototipo. Los defectos de las pruebas con usuarios se agregan al terminar la sección 4.

| ID | Defecto | Severidad | Responsable |
|---|---|---|---|
| DEF-01 | El catálogo simulado no incluye un paciente sin alergias ni un caso donde ninguna dieta sea segura | Mayor | Analista de requisitos |
| DEF-02 | Las alergias dependen de etiquetas simples; un registro en texto libre no se cruzaría bien | Mayor | Desarrollo |
| DEF-03 | La asignación no guarda fecha ni el médico que confirmó la alerta | Menor | Desarrollo |
| DEF-04 | La jerarquía visual no se ha probado con lectores de pantalla | Menor | Diseño / QA |
| DEF-05 | P4 tardó 97 s porque abrió la ficha técnica antes de comparar las dietas por la etiqueta «segura/con alerta»; la etiqueta debería ser más prominente para un usuario nuevo | Mayor | Diseño |
| DEF-06 | P2 dudó unos segundos sobre dónde iniciar el flujo al no tener un paciente preseleccionado; falta un texto guía en la pantalla inicial | Menor | Diseño |

Escala: **Crítico** (impide validar el requisito), **Mayor** (afecta la seguridad o el flujo principal), **Menor** (cosmético o de mejora).

## 6. Matriz de trazabilidad

| Criterio | Requisito | Elemento del prototipo | Prueba | Estado |
|---|---|---|---|---|
| CA1 | RF1 | Lista de dietas al seleccionar paciente | Seleccionar cada paciente y verificar la lista | Implementado |
| CA2 | RF2, RF3 | Etiqueta «CON ALERTA», alimento resaltado y ventana de confirmación | Asignar dieta con alérgeno | Implementado |
| CA3 | RF4 | Ficha técnica con barra de paciente fija | Abrir ficha y comprobar que el paciente sigue visible | Implementado |
| CA4 | RF5 | Orden por seguridad y prueba cronometrada | Prueba con usuarios (sección 4) | Validado parcialmente (4/5, 80 %) |

## 7. Decisión: el requisito queda validado, con reformulación de los criterios
El prototipo demuestra que la funcionalidad principal (RF1 a RF4) funciona sin errores críticos: en ningún caso se asignó una dieta insegura sin confirmación explícita. CA4 se cumplió en el 80 % de las pruebas (4 de 5); el caso que falló fue por un problema de jerarquía visual (DEF-05), no de seguridad clínica, así que no invalida la épica pero sí exige un ajuste de diseño antes de pasar a desarrollo. Además, los criterios de aceptación originales necesitan mayor precisión:

- **CA1 reformulado:** «Dado un paciente con al menos una enfermedad registrada, al seleccionarlo el sistema muestra en la misma pantalla todas las dietas asociadas, ordenadas con las seguras primero.»
- **CA2 reformulado:** «Si una dieta contiene un alimento al que el paciente es alérgico o incompatible, el sistema muestra una alerta con el nombre del alimento y exige confirmación explícita antes de asignarla.»
- **CA3 reformulado:** «La ficha técnica incluye los diez campos del catálogo y se abre sin ocultar los datos del paciente.»
- **CA4 reformulado:** «Un usuario nuevo, sin capacitación, asigna una dieta segura en menos de 90 s, y ninguna dieta con alerta se asigna sin confirmación.»
- **Término único:** usar «alérgeno/incompatibilidad» en toda la épica.
- **Caso faltante:** definir qué ve el médico si ninguna dieta es segura.

**Conclusión:** la épica EPC 28 queda **validada de forma condicional**. Se recomienda corregir DEF-05 y DEF-06 (jerarquía visual y guía inicial) y repetir la prueba de CA4 con un participante adicional antes del cierre definitivo del requisito.
