# ADR-001: Topologia Multiagente Coordenador + Especialistas via Sub-Agents

## Status
Aceito (Accepted)

## Contexto
O assistente virtual do Residencial Aurora precisa atender a múltiplos domínios (reservas de áreas comuns, portaria e visitantes, e dúvidas sobre regulamento). Carregar todas as tools e instruções em um único agente sobrecarrega a janela de contexto, aumenta o custo de inferência e eleva o risco de alucinações. O desafio exige explicitamente: *"um agente principal e pelo menos dois especialistas"*. Além disso, ações que exigem confirmação do morador (`request_confirmation`) pausam a execução e precisam ser retomadas diretamente no agente que solicitou a confirmação.

## Decisão
Adotamos o padrão **Coordenador + Especialistas via Sub-Agents** nativo do Google ADK (série 2, v2.2.0):
1. **`recepcao_aurora`** atua como o agente principal de entrada no `Runner`, realizando apenas a triagem e delegando chamadas via transferência nativa (`transfer_to_agent`).
2. Três sub-agents especializados:
   - `agente_reservas`: equipado com tools de reservas.
   - `agente_visitantes`: equipado com tools de portaria.
   - `agente_regulamento`: equipado com tool de consulta por capítulo.
3. Configuramos o `App` com `ResumabilityConfig(is_resumable=True)` e mantemos a transferência aberta (`disallow_transfer_to_parent=False`), assegurando que a resposta a uma confirmação pendente seja encaminhada diretamente ao subagente correto, inclusive após reinício com sessão persistida em SQLite.

## Consequências
- **Positivas**: Separação clara de responsabilidades; redução do tamanho dos prompts; preservação da retomada de execução de tools pausadas.
- **Negativas**: Pequeno overhead de transferência inicial de agente na primeira mensagem.
