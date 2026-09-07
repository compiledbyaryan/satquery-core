# Product requirements and current decisions

SatQuery is an interactive evidence-grounded remote-sensing workbench. Users supply an image or pair, ask a question, and receive textual/spatial outputs with confidence information and an observable tool trace.

## Mandatory acceptance matrix
| ID | Capability | Acceptance evidence |
|---|---|---|
| R1 | Single-image VQA across supported optical/multispectral and SAR routes | Actual specialist outputs and held-out evaluation |
| R2 | Captioning as the committed additional single task; grounding if validated | Evidence-backed caption; actual evaluated boxes/masks for grounding |
| R3 | Bi-temporal change understanding and CDVQA evaluation route | Correct temporal bindings, change outputs and prescribed test-split result |
| R4 | Co-registered optical/multispectral plus SAR joint extraction | Both sensors consumed; optical-only/SAR-only/paired ablations |
| R5 | At least one adapted visual/VL component | BigEarthNet.txt or permitted train-data manifest, checkpoint, reproducible training and held-out comparison |
| R6 | Automatic tool selection, sequencing, permitted parameters, execution | Plan, named inputs, exact tools/versions, outcomes and trace |
| R7 | GeoTIFF/TIFF; PNG/JPEG only allowed benchmark records | Server-side manifest and decode validation |
| R8 | GUI, visual evidence, uncertainty, report, code/models/tests/demo | Real end-to-end run and downloadable artifacts |

All capabilities are currently pending implementation except the supporting contract foundation. Do not represent mock UI, schema tests or public checkpoint availability as completion of R1-R8.

## Target release
A polished internal demonstration followed by a controlled scientist pilot. Start with built-up/water/land-cover interpretation and change. No claims of structural damage, causation, legality, exact material composition or future disaster state without the required evidence. No new LoRA training; a small visual projection/fusion/head is the first adaptation strategy.

Architecture: natural language -> typed plan -> compatibility checks -> registered specialists/GIS -> evidence graph -> claim checks -> map/report. The product runtime cannot modify source code or call arbitrary shell tools. Development coding agents operate separately.

Feature order: all mandatory tasks; robust input/failure handling; strong map-first UX; lightweight claim revision; targeted verification. Defer learned RL routing, arbitrary generated tools, a separate agent operating system, satellite purchasing and 3D reconstruction.

Numbers in UI fixtures are synthetic. Real confidence needs a calibration record; otherwise show the basis and limitations without invented percentages. GeoTIFF metadata presence does not prove registration or valid area units. Hidden ISRO/SAC annotations are unavailable. Final judging weights, deadline, exact GPU memory, data permissions and spending cap remain unconfirmed.

