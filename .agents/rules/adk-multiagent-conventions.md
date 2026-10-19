# Regra: Convenções de Agentes Google ADK v2 (adk-multiagent-conventions)

## Diretivas Obrigatórias
1. **Topologia Coordenador + Sub-Agents**:
   - O agente principal (`recepcao_aurora`) é a porta de entrada da sessão.
   - Os agentes de domínio (`agente_reservas`, `agente_visitantes`, `agente_regulamento`) devem ser configurados como `sub_agents` do agente principal.
   - A delegação ocorre via transferência de controle nativa (`transfer_to_agent`).
2. **Preservação de Retomada (Garantia 1 & Dicas do Desafio)**:
   - Configurar o `App` com `ResumabilityConfig(is_resumable=True)`.
   - Manter a transferência aberta (`disallow_transfer_to_parent=False`), assegurando que respostas a confirmações pendentes retornem diretamente ao sub-agent originário.
3. **Isolamento de Estado (Garantia 2)**:
   - NENHUMA tool de domínio pode receber o parâmetro `apartamento` como entrada selecionada pelo LLM.
   - O apartamento deve ser recuperado estritamente de `tool_context.state["apartamento"]`.
4. **Isolamento de Contexto do Regulamento (Garantia 4)**:
   - O agente principal `recepcao_aurora` NÃO PODE conter o texto do regulamento em suas instruções (`instruction`).
   - O especialista `agente_regulamento` contém apenas o sumário dos capítulos e utiliza a tool `consultar_capitulo_regulamento` para ler unicamente o capítulo necessário.
