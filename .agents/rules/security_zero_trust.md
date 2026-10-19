# Regra: Segurança Zero Trust e Proteção de Credenciais (security_zero_trust)

## Diretivas Obrigatórias
1. **Proteção Total de Segredos e Chaves de API**:
   - JAMAIS versione chaves de API (`GOOGLE_API_KEY`, `GEMINI_API_KEY`), tokens ou senhas no código, documentação, testes ou commits.
   - Todas as chaves devem ser lidas exclusivamente de variáveis de ambiente (`.env`).
   - O arquivo `.env` deve permanecer sempre no `.gitignore`.
2. **Conformidade em Exemplos e Testes**:
   - Ao escrever mocks, documentação ou exemplos, use placeholders de baixa entropia: `<SUA_CHAVE_AQUI>`, `REPLACE_WITH_YOUR_KEY`.
   - Nunca utilize strings com formatos realistas de tokens em arquivos versionados.
3. **Isolamento de Dados de Terceiros (Garantia 2)**:
   - Respostas do assistente e eventos da sessão nunca podem expor dados sensíveis ou códigos de reservas pertencentes a outros apartamentos (`RSV-4821`, `Marina Duarte`, etc.).
