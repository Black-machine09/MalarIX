# TODO (Malaria Triage AI - MVP)

- [ ] Atualizar `api/routes/predict.py` para diferenciar falhas de decodificação (decode_image) vs falhas de validação de qualidade (validate_image_quality).
- [ ] Retornar erros 422 específicos quando `scores` estiver vazio: `image_decode_failed` (se todas falharam decode) ou `image_quality_insufficient` (se decode ok mas qualidade rejeitou).
- [ ] Incluir contadores de falhas por tipo (decode/quality) e (se possível) razões de quality para facilitar tuning.
- [ ] Rodar novamente o curl de teste e validar resposta.

