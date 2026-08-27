# Evaluación del RAG

`questions.json` es el dataset manual de referencia. Cada pregunta está
asociada a los documentos que deben aparecer entre los primeros resultados.

La evaluación debe separar retrieval de generación:

1. Capturar para cada pregunta los chunks recuperados por Vectorize en un JSON
   con `question_id`, `content` y, si está disponible, `score`.
2. Ejecutar `rag_evaluator.py` de la skill `evaluate-rag` para medir relevancia,
   Precision@k, MRR y faithfulness sobre las respuestas obtenidas.
3. Comparar el reporte con el baseline después de modificar chunking, embeddings
   o prompts.

El dataset no llama a Workers AI ni consume tokens. Las pruebas remotas deben
vivir separadas bajo `api/tests/token/` y marcarse con `@pytest.mark.token`.
