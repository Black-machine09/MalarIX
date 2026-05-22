# TODO (Malaria Triage AI - MVP)

- [ ] Atualizar `api/routes/predict.py` para diferenciar falhas de decodificaeo (decode_image) vs falhas de validaeo de qualidade (validate_image_quality).
- [ ] Retornar erros 422 especficos quando `scores` estiver vazio: `image_decode_failed` (se todas falharam decode) ou `image_quality_insufficient` (se decode ok mas qualidade rejeitou).
- [ ] Incluir contadores de falhas por tipo (decode/quality) e (se possvel) razes de quality para facilitar tuning.
- [ ] Rodar novamente o curl de teste e validar resposta.

## Deploy / Render (startup)
- [ ] Ajustar `.gitignore` para no excluir o arquivo ONNX do repositrio (hoje o Render provavelmente no est recebendo `model/malaria_resnet18.onnx` no build).

