# Fase 02: Camada de Dados, Concorrência & Tools Determinísticas

## Objetivo
Implementar as tools Python determinísticas com suporte às garantias de negócio:
- Confirmação de taxa > 0 e autorização de visitantes (G1).
- Isolamento de apartamento obtido exclusivamente via `tool_context.state["apartamento"]` (G2).
- Gravação transacional com `BEGIN IMMEDIATE` e captura de `IntegrityError` com retorno de indisponibilidade tratada sem erro 500 (G5).
- Geração de códigos não-repetíveis registrados em `codigos_reserva_usados` (RN05).

## Step Implementations (SIs)
1. **SI-02-01**: Implementar `listar_areas_comuns()` e `consultar_minhas_reservas(tool_context: ToolContext)` em [`src/aurora/tools.py`](file:///e:/Projects/mba-ia-desafio-criacao-agente/src/aurora/tools.py).
2. **SI-02-02**: Implementar `verificar_disponibilidade_area(area: str, data: str)` retornando apenas booleano (sem vazar dados de terceiros).
3. **SI-02-03**: Implementar `reservar_area(area: str, data: str, tool_context: ToolContext)` com bifurcação de confirmação (taxa 0 grava direto, taxa > 0 pede confirmação) e gravação atômica `UNIQUE(area, data)`.
4. **SI-02-04**: Implementar `cancelar_minha_reserva(codigo: str, tool_context: ToolContext)` filtrando exclusivamente pelo apartamento da sessão e sem pedir confirmação.
5. **SI-02-05**: Implementar `listar_meus_visitantes(tool_context: ToolContext)` e `autorizar_visitante(nome: str, data: str, tool_context: ToolContext)` exigindo confirmação obrigatória.
6. **SI-02-06**: Criar testes automatizados em [`tests/test_tools.py`](file:///e:/Projects/mba-ia-desafio-criacao-agente/tests/test_tools.py).
