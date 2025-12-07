# SLIP-39 Implementation Plan

## Visão Geral

Este documento apresenta um plano detalhado, dividido em etapas incrementais, para implementar suporte a SLIP-39 no secreon. Cada etapa é independente e testável, permitindo desenvolvimento iterativo com entregas funcionais.

---

## FASE 1: Fundamentos e Infraestrutura
**Objetivo**: Estabelecer a base matemática e estruturas de dados necessárias

### Etapa 1.1: GF(256) Arithmetic Implementation
**Duração estimada**: 2-3 dias
**Prioridade**: CRÍTICA

**Tarefas**:
1. Criar módulo `src/slip39/gf256.py`
2. Implementar operações básicas de GF(256):
   - Adição (XOR)
   - Multiplicação usando polinômio Rijndael
   - Inverso multiplicativo (para divisão)
3. Pré-computar tabelas log/exp para otimização
4. Implementar interpolação de Lagrange sobre GF(256)

**Entregáveis**:
- [ ] `gf256.py` com funções: `add()`, `multiply()`, `divide()`, `interpolate()`
- [ ] Testes unitários para todas as operações
- [ ] Performance benchmark (deve ser rápido, <1ms para operações típicas)

**Critérios de Aceite**:
- Todos os testes passam
- Multiplicação/divisão corretas segundo tabela AES
- Interpolação recupera secret de shares válidos

**Dependências**: Nenhuma

---

### Etapa 1.2: RS1024 Checksum Implementation
**Duração estimada**: 2 dias
**Prioridade**: CRÍTICA

**Tarefas**:
1. Criar módulo `src/slip39/rs1024.py`
2. Implementar polinômio gerador para RS1024
3. Implementar funções de checksum:
   - `create_checksum(data, customization_string)`
   - `verify_checksum(data, customization_string)`
4. Suportar customization strings: "shamir" e "shamir_extendable"

**Entregáveis**:
- [ ] `rs1024.py` com funções de checksum
- [ ] Testes com valores conhecidos da especificação
- [ ] Verificação de detecção de erros (até 3 palavras)

**Critérios de Aceite**:
- Checksum compatível com implementação de referência
- Detecta até 3 erros com 100% de certeza
- Probabilidade <1e-9 de falhar em detectar mais erros

**Dependências**: Nenhuma

---

### Etapa 1.3: Wordlist Management
**Duração estimada**: 1 dia
**Prioridade**: ALTA

**Tarefas**:
1. Criar módulo `src/slip39/wordlist.py`
2. Incluir SLIP-39 wordlist oficial (1024 palavras)
3. Implementar conversões:
   - Palavras → índices
   - Índices → palavras
   - Inteiro → lista de índices
   - Lista de índices → inteiro

**Entregáveis**:
- [ ] `wordlist.py` com wordlist SLIP-39
- [ ] Funções de conversão
- [ ] Validação de prefixos únicos de 4 letras
- [ ] Testes de conversão bidirecional

**Critérios de Aceite**:
- Wordlist idêntica à especificação oficial
- Todos os prefixos de 4 letras são únicos
- Conversões bidirecionais sem perda

**Dependências**: Nenhuma

---

### Etapa 1.4: BIP-39 Support
**Duração estimada**: 1-2 dias
**Prioridade**: ALTA

**Tarefas**:
1. Criar módulo `src/slip39/bip39.py`
2. Incluir BIP-39 wordlist (English, 2048 palavras)
3. Implementar geração de mnemonic:
   - Gerar 256 bits de entropia
   - Calcular checksum (SHA-256)
   - Converter para 24 palavras
4. Implementar validação e conversão de mnemonic para entropy

**Entregáveis**:
- [ ] `bip39.py` com funções de geração e validação
- [ ] Testes com test vectors do BIP-39
- [ ] Função para gerar seed aleatória de 24 palavras

**Critérios de Aceite**:
- Geração compatível com BIP-39
- Validação de checksum funciona
- Conversão mnemonic → entropy → mnemonic preserva dados

**Dependências**: Nenhuma

---

## FASE 2: Criptografia e Secret Sharing
**Objetivo**: Implementar o núcleo do SLIP-39

### Etapa 2.1: Feistel Cipher Implementation
**Duração estimada**: 2-3 dias
**Prioridade**: CRÍTICA

**Tarefas**:
1. Criar módulo `src/slip39/cipher.py`
2. Implementar função de round usando PBKDF2-HMAC-SHA256
3. Implementar criptografia (4 rounds Feistel)
4. Implementar descriptografia (4 rounds reversos)
5. Suportar salt customization (ext flag)

**Entregáveis**:
- [ ] `cipher.py` com funções `encrypt()` e `decrypt()`
- [ ] Testes de round-trip (encrypt → decrypt = identity)
- [ ] Testes com diferentes iteration exponents
- [ ] Testes com/sem extendable flag

**Critérios de Aceite**:
- Encrypt/decrypt são inversos perfeitos
- Compatível com python-shamir-mnemonic
- Performance aceitável (~5-10s para e=1)

**Dependências**: Nenhuma (usa stdlib hashlib, hmac)

---

### Etapa 2.2: SLIP-39 Share Data Structure
**Duração estimada**: 2 dias
**Prioridade**: CRÍTICA

**Tarefas**:
1. Criar módulo `src/slip39/share.py`
2. Definir classe `Share` com todos os campos:
   - identifier, extendable, iteration_exponent
   - group_index, group_threshold, group_count
   - member_index, member_threshold
   - share_value
3. Implementar encoding: Share → mnemonic
4. Implementar decoding: mnemonic → Share
5. Implementar validações

**Entregáveis**:
- [ ] `share.py` com classe `Share`
- [ ] Métodos `to_mnemonic()` e `from_mnemonic()`
- [ ] Testes de encoding/decoding round-trip
- [ ] Validação de todos os campos

**Critérios de Aceite**:
- Share → mnemonic → Share preserva dados
- Checksum validado no decode
- Formato compatível com especificação

**Dependências**: 1.2 (RS1024), 1.3 (Wordlist)

---

### Etapa 2.3: SLIP-39 Core SSS Implementation
**Duração estimada**: 3-4 dias
**Prioridade**: CRÍTICA

**Tarefas**:
1. Criar módulo `src/slip39/shamir.py`
2. Implementar split sobre GF(256):
   - `split_secret(threshold, count, secret)` → shares
   - Byte-by-byte SSS
   - Incluir digest quando threshold ≥ 2
3. Implementar recover:
   - `recover_secret(shares)` → secret
   - Validar digest
   - Interpolação sobre GF(256)
4. Implementar esquema de dois níveis:
   - `split_ems(group_threshold, groups, ems)` → grouped shares
   - `recover_ems(grouped_shares)` → ems

**Entregáveis**:
- [ ] `shamir.py` com funções de split/recover
- [ ] Classe `EncryptedMasterSecret`
- [ ] Testes de split/recover round-trip
- [ ] Testes de threshold (T shares funcionam, T-1 falham)
- [ ] Testes de esquema de dois níveis

**Critérios de Aceite**:
- Qualquer conjunto de T shares recupera secret
- T-1 shares não recupera secret
- Digest detecta shares inválidas
- Compatível com python-shamir-mnemonic

**Dependências**: 1.1 (GF256), 2.1 (Cipher), 2.2 (Share)

---

### Etapa 2.4: High-Level API
**Duração estimada**: 2 dias
**Prioridade**: ALTA

**Tarefas**:
1. Implementar funções de alto nível em `shamir.py`:
   - `generate_mnemonics(group_threshold, groups, master_secret, passphrase, ...)`
   - `combine_mnemonics(mnemonics, passphrase)`
2. Implementar validações de entrada
3. Implementar geração de identifier aleatório
4. Tratamento de erros user-friendly

**Entregáveis**:
- [ ] API de alto nível documentada
- [ ] Testes end-to-end (generate → combine)
- [ ] Validação de parâmetros
- [ ] Mensagens de erro claras

**Critérios de Aceite**:
- API simples e intuitiva
- Validações previnem uso incorreto
- Compatível com test vectors oficiais

**Dependências**: 2.3 (Core SSS)

---

## FASE 3: Integração CLI e User Experience
**Objetivo**: Tornar a funcionalidade acessível via linha de comando

### Etapa 3.1: CLI - Generate Seed Command
**Duração estimada**: 1 dia
**Prioridade**: ALTA

**Tarefas**:
1. Criar `src/slip39/cli.py` ou estender `secreon.py`
2. Implementar comando `slip39 generate-seed`:
   - Gerar BIP-39 mnemonic de 24 palavras
   - Salvar em arquivo ou exibir
   - Opção de fornecer entropy customizada

**Entregáveis**:
- [ ] Comando `secreon slip39 generate-seed`
- [ ] Opções: `--out`, `--entropy`
- [ ] Warnings sobre guardar seed com segurança

**Critérios de Aceite**:
- Gera seed BIP-39 válida
- Salva corretamente em arquivo
- UI clara e intuitiva

**Dependências**: 1.4 (BIP-39)

---

### Etapa 3.2: CLI - Generate Shares Command
**Duração estimada**: 2-3 dias
**Prioridade**: CRÍTICA

**Tarefas**:
1. Implementar comando `slip39 generate`:
   - Aceitar master secret de múltiplas fontes:
     - `--seed-file` (BIP-39 mnemonic)
     - `--master-secret` (hex string)
   - Esquema simples: `--threshold`, `--shares`
   - Esquema avançado: `--group-threshold`, `--group` (múltiplo)
   - Opções: `--passphrase`, `--iteration-exponent`, `--extendable`
2. Exibir shares como mnemonics
3. Salvar em arquivos individuais ou JSON

**Entregáveis**:
- [ ] Comando `secreon slip39 generate`
- [ ] Suporte a esquemas simples e avançados
- [ ] Output legível e organizado
- [ ] Opção de split shares em arquivos separados

**Critérios de Aceite**:
- Gera shares válidas de todas as fontes
- UI intuitiva para ambos os esquemas
- Arquivos de output bem organizados
- Warnings sobre distribuição segura

**Dependências**: 2.4 (High-Level API), 3.1 (Generate Seed)

---

### Etapa 3.3: CLI - Recover Command
**Duração estimada**: 2 dias
**Prioridade**: CRÍTICA

**Tarefas**:
1. Implementar comando `slip39 recover`:
   - Aceitar mnemonics de múltiplas fontes:
     - Arquivos individuais
     - Diretório com shares
     - Input interativo
   - Opção `--passphrase`
   - Validar shares antes de tentar recuperar
2. Informar progresso (quantas shares/grupos faltam)
3. Exibir master secret ou salvar em arquivo

**Entregáveis**:
- [ ] Comando `secreon slip39 recover`
- [ ] Múltiplas formas de input
- [ ] Feedback de progresso
- [ ] Validação e mensagens de erro claras

**Critérios de Aceite**:
- Recupera master secret de shares válidas
- Detecta shares insuficientes ou inválidas
- UI clara com feedback de progresso
- Não exibe secret por padrão (opção `--show`)

**Dependências**: 2.4 (High-Level API)

---

### Etapa 3.4: CLI - Utility Commands
**Duração estimada**: 1-2 dias
**Prioridade**: MÉDIA

**Tarefas**:
1. Implementar comando `slip39 info`:
   - Exibir informações sobre uma share
   - Mostrar parâmetros (threshold, grupos, etc.)
   - Não revelar share value
2. Implementar comando `slip39 validate`:
   - Validar mnemonics sem recuperar secret
   - Verificar checksums
   - Verificar compatibilidade entre shares

**Entregáveis**:
- [ ] Comando `secreon slip39 info`
- [ ] Comando `secreon slip39 validate`
- [ ] Output formatado e legível

**Critérios de Aceite**:
- Exibe informações úteis sem comprometer segurança
- Validação detecta problemas comuns
- Ajuda usuários a organizar shares

**Dependências**: 2.2 (Share)

---

## FASE 4: Testes e Qualidade
**Objetivo**: Garantir correção, segurança e interoperabilidade

### Etapa 4.1: Official Test Vectors
**Duração estimada**: 2 dias
**Prioridade**: CRÍTICA

**Tarefas**:
1. Baixar test vectors oficiais: vectors.json
2. Criar `tests/slip39/test_vectors.py`
3. Implementar testes para todos os casos:
   - Valid mnemonics (vários tamanhos)
   - Invalid mnemonics (vários tipos de erro)
   - Group sharing
   - Passphrases
   - Extendable backups

**Entregáveis**:
- [ ] `test_vectors.py` com todos os casos oficiais
- [ ] 100% dos test vectors passam
- [ ] Relatório de compatibilidade

**Critérios de Aceite**:
- Todos os test vectors válidos geram resultado esperado
- Todos os test vectors inválidos são detectados
- Compatibilidade 100% com especificação

**Dependências**: 2.4 (High-Level API)

---

### Etapa 4.2: Cross-Implementation Testing
**Duração estimada**: 2-3 dias
**Prioridade**: ALTA

**Tarefas**:
1. Criar testes de interoperabilidade com python-shamir-mnemonic:
   - Gerar shares no secreon, recuperar com python-shamir-mnemonic
   - Gerar shares no python-shamir-mnemonic, recuperar com secreon
2. Testar múltiplos cenários:
   - Diferentes tamanhos de secret
   - Diferentes thresholds
   - Com/sem passphrase
   - Grupos múltiplos
3. Documentar eventuais incompatibilidades

**Entregáveis**:
- [ ] Script de testes cruzados
- [ ] Relatório de compatibilidade
- [ ] Fix de incompatibilidades encontradas

**Critérios de Aceite**:
- Interoperabilidade 100% com python-shamir-mnemonic
- Shares são intercambiáveis entre implementações
- Documentação de diferenças (se houver)

**Dependências**: 2.4 (High-Level API), 4.1 (Test Vectors)

---

### Etapa 4.3: Property-Based Testing
**Duração estimada**: 2 dias
**Prioridade**: MÉDIA

**Tarefas**:
1. Usar `hypothesis` para testes property-based
2. Testar propriedades fundamentais:
   - Round-trip: generate → recover = identity
   - Threshold: T shares funcionam, T-1 não
   - Segurança: shares aleatórias não revelam informação
   - Independência: mudança em 1 share não afeta outras
3. Testar edge cases gerados automaticamente

**Entregáveis**:
- [ ] Testes property-based com `hypothesis`
- [ ] Cobertura de propriedades fundamentais
- [ ] Relatório de edge cases encontrados

**Critérios de Aceite**:
- Todas as propriedades verificadas
- Nenhum edge case quebra o sistema
- Confiança alta na correção

**Dependências**: 2.4 (High-Level API)

---

### Etapa 4.4: Security Audit Preparation
**Duração estimada**: 2-3 dias
**Prioridade**: ALTA

**Tarefas**:
1. Code review focado em segurança:
   - Uso correto de aleatoriedade (secrets.token_bytes)
   - Não vazar secrets em logs/erros
   - Validação de entrada completa
   - Side-channel considerations (Python limitation)
2. Verificar tratamento de casos extremos
3. Documentar decisões de segurança
4. Preparar checklist para auditoria externa

**Entregáveis**:
- [ ] Relatório de code review de segurança
- [ ] Lista de melhorias implementadas
- [ ] Documentação de decisões de segurança
- [ ] Checklist para auditoria externa

**Critérios de Aceite**:
- Nenhuma vulnerabilidade óbvia encontrada
- Seguir best practices de criptografia
- Código preparado para auditoria

**Dependências**: Todas as etapas anteriores

---

## FASE 5: Documentação e Release
**Objetivo**: Preparar para produção e uso público

### Etapa 5.1: User Documentation
**Duração estimada**: 2-3 dias
**Prioridade**: ALTA

**Tarefas**:
1. Escrever tutorial completo no README
2. Criar guia de início rápido
3. Documentar casos de uso comuns
4. Escrever FAQ
5. Documentar diferenças entre SSS clássico e SLIP-39
6. Best practices de segurança

**Entregáveis**:
- [ ] Tutorial no README atualizado
- [ ] Guia de início rápido
- [ ] Documentação de casos de uso
- [ ] FAQ
- [ ] Guia de segurança

**Critérios de Aceite**:
- Documentação clara e compreensível
- Cobrir casos de uso principais
- Warnings de segurança apropriados

**Dependências**: 3.3 (CLI completa)

---

### Etapa 5.2: Technical Documentation
**Duração estimada**: 2 dias
**Prioridade**: MÉDIA

**Tarefas**:
1. Atualizar docs/TECHNICAL.md
2. Documentar arquitetura do SLIP-39
3. Documentar APIs de cada módulo
4. Criar diagramas de fluxo
5. Documentar decisões de design

**Entregáveis**:
- [ ] TECHNICAL.md atualizado
- [ ] Documentação de arquitetura
- [ ] API reference completa
- [ ] Diagramas de fluxo

**Critérios de Aceite**:
- Desenvolvedores conseguem entender código
- APIs bem documentadas
- Decisões de design justificadas

**Dependências**: Todas as fases anteriores

---

### Etapa 5.3: Release Preparation
**Duração estimada**: 1-2 dias
**Prioridade**: ALTA

**Tarefas**:
1. Atualizar CHANGELOG.md
2. Criar RELEASE_NOTES para versão SLIP-39
3. Verificar cobertura de testes
4. Rodar linters e formatters
5. Preparar release notes para GitHub

**Entregáveis**:
- [ ] CHANGELOG atualizado
- [ ] RELEASE_NOTES específicas
- [ ] Cobertura de testes >80%
- [ ] Código formatado e sem warnings

**Critérios de Aceite**:
- Changelog completo e claro
- Testes com boa cobertura
- Código limpo e sem warnings

**Dependências**: 5.1 (User Docs), 5.2 (Tech Docs)

---

### Etapa 5.4: Examples and Demos
**Duração estimada**: 1 dia
**Prioridade**: BAIXA

**Tarefas**:
1. Criar exemplos práticos em examples/
2. Script de demo para casos comuns
3. Exemplo de uso como biblioteca Python
4. Video ou GIF demonstrando CLI

**Entregáveis**:
- [ ] Scripts de exemplo
- [ ] Demo script
- [ ] Exemplo de uso como lib
- [ ] Material visual (opcional)

**Critérios de Aceite**:
- Exemplos funcionam out-of-the-box
- Cobrem casos de uso principais
- Fácil de seguir para iniciantes

**Dependências**: 5.1 (User Docs)

---

## Estimativa de Tempo Total

### Por Fase:
- **Fase 1** (Fundamentos): 6-8 dias
- **Fase 2** (Core SSS): 9-13 dias
- **Fase 3** (CLI): 6-8 dias
- **Fase 4** (Testes): 8-10 dias
- **Fase 5** (Documentação): 6-8 dias

### Total: 35-47 dias de desenvolvimento

### Com dedicação:
- **Full-time** (8h/dia): 5-6 semanas
- **Part-time** (4h/dia): 10-12 semanas
- **Casual** (2h/dia): 20-24 semanas

---

## Priorização para MVP

Se o objetivo for entregar um MVP funcional rapidamente, a seguinte ordem é recomendada:

### MVP Path (2-3 semanas full-time):
1. ✅ **Etapa 1.1**: GF(256) - CRÍTICO
2. ✅ **Etapa 1.2**: RS1024 - CRÍTICO
3. ✅ **Etapa 1.3**: Wordlist - CRÍTICO
4. ✅ **Etapa 1.4**: BIP-39 - ALTO
5. ✅ **Etapa 2.1**: Cipher - CRÍTICO
6. ✅ **Etapa 2.2**: Share - CRÍTICO
7. ✅ **Etapa 2.3**: Core SSS - CRÍTICO
8. ✅ **Etapa 2.4**: High-Level API - ALTO
9. ✅ **Etapa 3.1**: Generate Seed CLI - ALTO
10. ✅ **Etapa 3.2**: Generate Shares CLI - CRÍTICO
11. ✅ **Etapa 3.3**: Recover CLI - CRÍTICO
12. ✅ **Etapa 4.1**: Test Vectors - CRÍTICO
13. ✅ **Etapa 5.1**: User Docs (básico) - ALTO

O restante pode ser adicionado iterativamente após o MVP.

---

## Riscos e Mitigações

### Risco 1: Complexidade da Especificação
**Probabilidade**: Alta | **Impacto**: Alto

**Mitigação**:
- Implementação incremental com testes a cada etapa
- Usar python-shamir-mnemonic como referência
- Test vectors oficiais desde o início
- Code review detalhado

### Risco 2: Bugs de Criptografia
**Probabilidade**: Média | **Impacto**: Crítico

**Mitigação**:
- Seguir implementação de referência fielmente
- Testes extensivos (unit, integration, property-based)
- Cross-implementation testing
- Auditoria de segurança antes do release

### Risco 3: Performance Insatisfatória
**Probabilidade**: Baixa | **Impacto**: Médio

**Mitigação**:
- Pré-computar tabelas (log/exp para GF256)
- Permitir configuração de iteration exponent
- Benchmarking em cada etapa
- Otimizações após MVP funcional

### Risco 4: Incompatibilidade com Outras Implementações
**Probabilidade**: Média | **Impacto**: Alto

**Mitigação**:
- Testes cruzados frequentes
- Seguir especificação rigorosamente
- Usar mesmos test vectors
- Validação com múltiplas implementações (Trezor, Ledger, etc.)

---

## Checkpoints de Validação

### Checkpoint 1: Após Fase 1
**Validar**: Infraestrutura matemática funciona
- [ ] GF(256) passa testes de aritmética
- [ ] RS1024 detecta erros corretamente
- [ ] Wordlists completas e corretas

### Checkpoint 2: Após Fase 2
**Validar**: Core SSS funciona
- [ ] Generate → recover funciona (round-trip)
- [ ] Threshold respeitado (T ok, T-1 falha)
- [ ] Digest detecta shares inválidas

### Checkpoint 3: Após Fase 3
**Validar**: CLI funcional
- [ ] Usuário consegue gerar seed
- [ ] Usuário consegue criar shares
- [ ] Usuário consegue recuperar secret

### Checkpoint 4: Após Fase 4
**Validar**: Qualidade e compatibilidade
- [ ] Todos test vectors oficiais passam
- [ ] Interoperável com python-shamir-mnemonic
- [ ] Property tests passam

### Checkpoint 5: Após Fase 5
**Validar**: Pronto para release
- [ ] Documentação completa
- [ ] Código limpo e bem organizado
- [ ] Exemplos funcionais

---

## Critérios de Sucesso Final

### Must Have (Requisitos Mínimos):
- ✅ Geração de BIP-39 seed de 24 palavras
- ✅ Conversão BIP-39 → master secret
- ✅ Geração de SLIP-39 shares (esquema simples T-of-N)
- ✅ Recuperação de master secret de shares
- ✅ Passar todos os test vectors oficiais básicos
- ✅ CLI funcional para operações básicas
- ✅ Documentação de uso

### Should Have (Altamente Desejável):
- ✅ Esquema de dois níveis (grupos)
- ✅ Suporte a passphrase
- ✅ Interoperabilidade com python-shamir-mnemonic
- ✅ Property-based tests
- ✅ Documentação técnica completa

### Nice to Have (Opcional):
- ⭕ Utility commands (info, validate)
- ⭕ Exemplos e demos
- ⭕ Material visual
- ⭕ Auditoria de segurança externa

---

## Recursos Necessários

### Ferramentas de Desenvolvimento:
- Python 3.8+
- pytest (testes)
- hypothesis (property-based testing)
- mypy (type checking)
- black/ruff (formatação)

### Recursos Externos:
- SLIP-39 specification
- python-shamir-mnemonic (referência e testes cruzados)
- Test vectors oficiais
- BIP-39/BIP-32 specifications

### Hardware:
- Máquina de desenvolvimento (qualquer PC moderno serve)
- Opcional: Hardware wallet para testes de interoperabilidade

---

## Próximos Passos Imediatos

### Para Começar o Desenvolvimento:

1. **Setup Inicial** (30 min):
   ```bash
   mkdir -p src/slip39 tests/slip39
   touch src/slip39/__init__.py tests/slip39/__init__.py
   pip install pytest hypothesis
   ```

2. **Começar pela Etapa 1.1** (GF256):
   - Criar `src/slip39/gf256.py`
   - Implementar operações básicas
   - Criar `tests/slip39/test_gf256.py`
   - Passar todos os testes

3. **Iterar pelas Etapas**:
   - Completar uma etapa por vez
   - Testar exaustivamente antes de prosseguir
   - Documentar à medida que avança

4. **Checkpoints Regulares**:
   - Validar após cada fase
   - Ajustar plano se necessário
   - Manter stakeholders informados

---

## Conclusão

Este plano fornece um roadmap detalhado para implementar SLIP-39 no secreon de forma incremental e testável. Cada etapa é independente e produz artefatos verificáveis, permitindo desenvolvimento iterativo com entregas funcionais.

O MVP pode ser entregue em 2-3 semanas com dedicação full-time, e a implementação completa em 5-6 semanas. A priorização por fases permite entregar valor rapidamente enquanto constrói uma base sólida para funcionalidades avançadas.

---

**Última Atualização**: 2025-12-06  
**Status**: READY FOR DEVELOPMENT

