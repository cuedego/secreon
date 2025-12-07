# Entendimento do Desenvolvimento da Feature SLIP-39

## Resumo Executivo

O secreon é uma ferramenta para armazenamento seguro de secrets usando Shamir's Secret Sharing (SSS). A implementação atual usa SSS clássico com aritmética sobre campos primos grandes. Este documento apresenta meu entendimento sobre adicionar suporte a **SLIP-39**, um padrão moderno para backup de wallets cripto usando SSS com mnemonics human-readable.

---

## Contexto Técnico

### Estado Atual do Secreon

O secreon implementa:
- **SSS Clássico**: Divisão de secrets em shares usando polinômios sobre campo primo (2^2203-1)
- **Formato de Shares**: Pares (x, y) serializados em JSON
- **KDF**: Suporte a SHA-256 e PBKDF2 para derivação de keys de passphrases
- **CLI Simples**: Comandos `generate` e `recover`

**Limitações**:
- Shares são números grandes, não human-friendly
- Não é interoperável com wallets cripto modernas
- Não suporta esquemas hierárquicos (grupos)

### SLIP-39: O Padrão

**SLIP-39** (Shamir's Secret-Sharing for Mnemonic Codes) é um padrão da SatoshiLabs para backup de wallets BIP-32 usando SSS. Principais características:

1. **Mnemonics Human-Readable**: 
   - Shares codificados como 20-33 palavras (não números grandes)
   - Wordlist de 1024 palavras (10 bits por palavra)
   - Prefixos únicos de 4 letras para facilitar entrada

2. **Checksum Forte**:
   - Reed-Solomon RS1024 com 3 palavras de checksum
   - Detecta até 3 erros com certeza
   - <1e-9 chance de falhar em detectar mais erros

3. **Criptografia do Master Secret**:
   - Feistel cipher de 4 rounds com PBKDF2
   - Suporte a passphrase opcional
   - Iterações configuráveis (10000×2^e)

4. **Esquema de Dois Níveis**:
   - **Grupos**: GT-of-G (ex: 2 de 3 grupos)
   - **Membros**: Ti-of-Ni para cada grupo (ex: 3 de 5 membros)
   - Permite políticas de recuperação flexíveis

5. **GF(256) ao invés de Campo Primo**:
   - Aritmética byte-oriented (mais simples)
   - SSS aplicado byte-a-byte
   - Compatível com AES (mesmo polinômio irredutível)

6. **Digest de Verificação**:
   - Quando threshold ≥ 2, inclui digest do secret
   - Detecta shares maliciosas ou corrompidas
   - Digest = HMAC-SHA256(random_part, secret)

### Por que SLIP-39 é Importante?

- **Interoperabilidade**: Compatível com Trezor, Ledger, Electrum, Sparrow Wallet
- **Standard**: Especificação aberta e estável
- **UX**: Mnemonics são mais amigáveis que números grandes
- **Flexibilidade**: Esquema de dois níveis permite políticas sofisticadas
- **Segurança**: Checksum forte + digest + criptografia

---

## Análise Técnica Profunda

### Diferenças Fundamentais: SSS Clássico vs SLIP-39

| Aspecto | SSS Clássico (Secreon) | SLIP-39 |
|---------|------------------------|---------|
| **Campo Matemático** | GF(p) - primo grande (2^2203-1) | GF(256) - 256 elementos |
| **Operações** | Aritmética modular inteira | Aritmética polinomial byte-oriented |
| **Formato de Share** | (x, y) como inteiros grandes | Mnemonic de 20-33 palavras |
| **Encoding** | JSON com números | Wordlist de 1024 palavras |
| **Checksum** | Nenhum (ou opcional) | RS1024 obrigatório |
| **Criptografia** | Opcional (KDF) | Feistel cipher obrigatório |
| **Digest** | Não | Sim (para threshold ≥ 2) |
| **Níveis** | Único (T-of-N) | Dois (grupos + membros) |
| **Interoperabilidade** | Nenhuma | Standard, multi-wallet |

### Desafios Técnicos

#### 1. GF(256) Arithmetic
**Complexidade**: MÉDIA

GF(256) usa representação polinomial com operações módulo x^8 + x^4 + x^3 + x + 1:
- **Adição**: XOR (trivial)
- **Multiplicação**: Shift-and-XOR com redução polinomial
- **Divisão**: Inverso multiplicativo (usar tabelas log/exp)

**Solução**:
- Pré-computar tabelas de logaritmo e exponencial (256 entradas cada)
- Multiplicação: `exp[(log[a] + log[b]) % 255]`
- Divisão: `exp[(log[a] - log[b]) % 255]`
- Interpolação de Lagrange adaptada para GF(256)

**Referência**: Implementação em `python-shamir-mnemonic/shamir.py`

#### 2. RS1024 Checksum
**Complexidade**: MÉDIA-ALTA

Reed-Solomon sobre GF(1024) para detecção de erros:
- Código MDS (Maximum Distance Separable)
- 3 palavras de checksum = 30 bits
- Polinômio gerador sobre GF(1024) com raiz primitiva

**Solução**:
- Implementar como BCH code (visão alternativa de Reed-Solomon)
- Seguir implementação de referência fielmente
- Testes com valores conhecidos da especificação

**Referência**: `python-shamir-mnemonic/rs1024.py`

#### 3. Feistel Cipher com PBKDF2
**Complexidade**: MÉDIA

Criptografia do master secret em 4 rounds:
- Cada round usa PBKDF2-HMAC-SHA256
- Salt depende do `ext` flag:
  - ext=0: `"shamir" || identifier || R`
  - ext=1: apenas `R`
- Password: `round_number || passphrase`

**Solução**:
- Usar `hashlib.pbkdf2_hmac` da stdlib
- Implementar Feistel network simples (L, R swap + XOR)
- Garantir simetria (encrypt/decrypt são reversos)

**Referência**: `python-shamir-mnemonic/cipher.py`

#### 4. Esquema de Dois Níveis
**Complexidade**: ALTA

Hierarquia: EMS → Group Shares → Member Shares

```
Master Secret
    ↓ (encrypt)
Encrypted Master Secret (EMS)
    ↓ (split GT-of-G)
Group Share 1, ..., Group Share G
    ↓ (split T1-of-N1, ..., TG-of-NG)
Member Shares
```

**Solução**:
- Implementar split/recover recursivamente
- Validar consistência de parâmetros entre shares
- Suportar esquema simples (1 grupo) como caso especial

#### 5. Mnemonic Encoding/Decoding
**Complexidade**: MÉDIA

Cada share tem estrutura complexa de campos:

```
[id 15b][ext 1b][e 4b][GI 4b][GT 4b][G 4b][I 4b][T 4b][padding + share_value][checksum 30b]
```

Conversão: bits → palavras (cada 10 bits = 1 palavra)

**Solução**:
- Implementar packing/unpacking bit-oriented
- Validar padding (deve ser zeros e ≤ 8 bits)
- Seguir ordem da especificação rigorosamente

**Referência**: `python-shamir-mnemonic/share.py`

---

## Arquitetura Proposta

### Estrutura de Módulos

```
secreon/
├── src/
│   ├── sss.py              # Existing SSS (mantém compatibilidade)
│   └── slip39/             # Nova implementação SLIP-39
│       ├── __init__.py     # API pública
│       ├── wordlist.py     # SLIP-39 + BIP-39 wordlists
│       ├── bip39.py        # BIP-39 mnemonic generation
│       ├── gf256.py        # GF(256) arithmetic
│       ├── rs1024.py       # RS1024 checksum
│       ├── cipher.py       # Feistel cipher / encryption
│       ├── share.py        # Share data structure + encoding
│       ├── shamir.py       # SLIP-39 SSS core
│       └── cli.py          # CLI commands
└── tests/
    ├── test_sss.py         # Existing tests
    └── slip39/
        ├── test_gf256.py
        ├── test_rs1024.py
        ├── test_cipher.py
        ├── test_share.py
        ├── test_shamir.py
        └── test_vectors.py # Official SLIP-39 test vectors
```

### Separação de Responsabilidades

#### Camada 1: Matemática Fundamental
- `gf256.py`: Operações de campo, interpolação
- `rs1024.py`: Checksum e validação

#### Camada 2: Criptografia
- `cipher.py`: Encrypt/decrypt master secret
- `wordlist.py`: Conversões palavra ↔ índice

#### Camada 3: Secret Sharing
- `shamir.py`: Split/recover sobre GF(256)
- `share.py`: Estrutura de dados e encoding

#### Camada 4: BIP-39 Integration
- `bip39.py`: Geração e validação de seed phrases

#### Camada 5: User Interface
- `cli.py`: Commands para usuário final

### Fluxo de Dados

#### Generate:
```
BIP-39 Mnemonic (ou hex)
    ↓
Master Secret (entropy)
    ↓ (+ passphrase, identifier, e)
Encrypted Master Secret
    ↓ (split GT-of-G)
Group Shares
    ↓ (split Ti-of-Ni per group)
Member Shares (bytes)
    ↓ (encode)
SLIP-39 Mnemonics (palavras)
```

#### Recover:
```
SLIP-39 Mnemonics (palavras)
    ↓ (decode)
Member Shares (bytes)
    ↓ (recover Ti-of-Ni per group)
Group Shares
    ↓ (recover GT-of-G)
Encrypted Master Secret
    ↓ (decrypt with passphrase)
Master Secret
    ↓ (optional)
BIP-39 Mnemonic
```

---

## Estratégia de Implementação

### Abordagem: Bottom-Up com Validação Incremental

1. **Fundamentos Primeiro**: GF(256), RS1024, wordlists
   - Cada módulo testado isoladamente
   - Validação com valores conhecidos da especificação

2. **Core SSS em Seguida**: Split/recover sobre GF(256)
   - Testes de round-trip
   - Validação de threshold

3. **Criptografia e Encoding**: Cipher + Share structure
   - Testes de encrypt/decrypt
   - Testes de encoding/decoding

4. **Alto Nível e CLI**: API amigável + interface de usuário
   - Testes end-to-end
   - UX validation

5. **Interoperabilidade**: Testes cruzados com outras implementações
   - python-shamir-mnemonic
   - Test vectors oficiais

### Princípios de Desenvolvimento

1. **Test-Driven Development (TDD)**:
   - Escrever testes antes de implementação
   - Usar test vectors oficiais como guia
   - 100% cobertura de funções críticas

2. **Compatibility First**:
   - Seguir especificação SLIP-39 rigorosamente
   - Usar mesmos nomes de variáveis/funções que a spec
   - Validar contra python-shamir-mnemonic frequentemente

3. **Security by Design**:
   - Usar `secrets` module (não `random`)
   - Validar todas as entradas
   - Não logar/exibir secrets inadvertidamente
   - Clear memory onde possível (Python limitation)

4. **Incremental Delivery**:
   - MVP funcional em 2-3 semanas
   - Features avançadas iterativamente
   - Cada fase entrega valor

---

## Casos de Uso e Exemplos

### Caso 1: Backup Pessoal Simples
**Cenário**: Usuário quer proteger wallet pessoal com redundância

**Setup**:
```bash
# Gerar seed BIP-39
secreon slip39 generate-seed --out my-seed.txt

# Criar 3-of-5 shares
secreon slip39 generate --seed-file my-seed.txt --threshold 3 --shares 5 --out shares/

# Distribuir:
# - 1 em casa
# - 1 no trabalho
# - 1 no cofre do banco
# - 2 com amigos de confiança
```

**Recuperação**:
```bash
# Reunir 3 shares qualquer
secreon slip39 recover --mnemonics shares/share-1.txt shares/share-3.txt shares/share-5.txt
```

### Caso 2: Backup Familiar (Dois Níveis)
**Cenário**: Você pode recuperar sozinho OU família pode recuperar juntos

**Setup**:
```bash
secreon slip39 generate --seed-file my-seed.txt \
  --group-threshold 1 \
  --group 2 2 \  # Você: 2-of-2 (ambos necessários)
  --group 3 5 \  # Família: 3-of-5
  --out shares/

# Você guarda Group 1 shares (2 locais diferentes)
# Família recebe Group 2 shares (5 pessoas)
```

**Recuperação**:
- **Você sozinho**: Usa 2 shares do Group 1
- **Família**: Reúne 3 shares do Group 2

### Caso 3: Corporate Multi-Sig
**Cenário**: Empresa precisa aprovação de múltiplos departamentos

**Setup**:
```bash
secreon slip39 generate --master-secret <hex> \
  --group-threshold 2 \
  --group 2 3 \  # Diretores: 2-of-3
  --group 3 5 \  # Técnicos: 3-of-5
  --group 2 3 \  # Compliance: 2-of-3
  --passphrase "company-master-key" \
  --out shares/
```

**Recuperação**: Qualquer 2 grupos completos + passphrase

---

## Riscos e Mitigações

### Risco 1: Bugs Criptográficos
**Probabilidade**: MÉDIA | **Impacto**: CRÍTICO

**Mitigações**:
- Seguir implementação de referência (python-shamir-mnemonic)
- Testes extensivos (unit, integration, property-based)
- Code review focado em segurança
- Validação com test vectors oficiais
- Cross-implementation testing
- Auditoria externa (desejável)

### Risco 2: Incompatibilidade
**Probabilidade**: MÉDIA | **Impacto**: ALTO

**Mitigações**:
- Seguir especificação SLIP-39 rigorosamente
- Testes cruzados com python-shamir-mnemonic
- Usar mesmos test vectors
- Validar com hardware wallets (Trezor/Ledger) se possível

### Risco 3: Complexidade para Usuários
**Probabilidade**: ALTA | **Impacto**: MÉDIO

**Mitigações**:
- Modo simples por padrão (T-of-N, 1 grupo)
- Documentação clara com exemplos
- CLI intuitiva com validação de entrada
- Warnings sobre distribuição de shares
- Tutorial passo-a-passo

### Risco 4: Performance
**Probabilidade**: BAIXA | **Impacto**: BAIXO

**Mitigações**:
- PBKDF2 dominante (esperado, parte da segurança)
- Pré-computar tabelas (GF256)
- Permitir configuração de iteration exponent
- Benchmarking contínuo

---

## Critérios de Sucesso

### Técnicos:
- ✅ Passa 100% dos test vectors oficiais
- ✅ Interoperável com python-shamir-mnemonic
- ✅ Cobertura de testes >80%
- ✅ Sem vulnerabilidades óbvias (code review)
- ✅ Performance aceitável (<10s para operações)

### Funcionais:
- ✅ Usuário consegue gerar BIP-39 seed
- ✅ Usuário consegue criar SLIP-39 shares (simples e avançado)
- ✅ Usuário consegue recuperar master secret
- ✅ Suporte a passphrase
- ✅ CLI intuitiva

### Qualidade:
- ✅ Documentação completa (user + tech)
- ✅ Código limpo e bem organizado
- ✅ Type hints completos
- ✅ Exemplos funcionais

---

## Estimativas e Timeline

### MVP (Funcionalidade Básica):
**Tempo**: 2-3 semanas full-time (80-120 horas)

**Inclui**:
- GF(256), RS1024, wordlists
- Core SSS sobre GF(256)
- Cipher + Share encoding
- CLI básica (generate-seed, generate, recover)
- Test vectors oficiais básicos
- Documentação de uso

### Feature Completa:
**Tempo**: 5-6 semanas full-time (200-240 horas)

**Inclui tudo do MVP, mais**:
- Esquema de dois níveis completo
- Passphrase e iteration exponent configurável
- Utility commands (info, validate)
- Cross-implementation testing
- Property-based tests
- Documentação técnica completa
- Exemplos e demos
- Preparação para auditoria

### Part-Time:
- **4h/dia**: ~10-12 semanas para feature completa
- **2h/dia**: ~20-24 semanas para feature completa

---

## Próximos Passos Recomendados

### Imediato (Antes de Começar):
1. ✅ **Review desta documentação** com stakeholders
2. ✅ **Setup do ambiente** de desenvolvimento
3. ✅ **Download de recursos**:
   - SLIP-39 wordlist
   - BIP-39 wordlist
   - Test vectors oficiais
   - python-shamir-mnemonic (referência)

### Primeira Semana:
1. **Dia 1-2**: Implementar GF(256) + testes
2. **Dia 3**: Implementar RS1024 + testes
3. **Dia 4**: Implementar wordlists + testes
4. **Dia 5**: Review e ajustes da Fase 1

### Segunda Semana:
1. **Dia 1-2**: Implementar Feistel cipher + testes
2. **Dia 3-4**: Implementar Share structure + encoding
3. **Dia 5**: Implementar core SSS sobre GF(256)

### Terceira Semana:
1. **Dia 1**: BIP-39 support
2. **Dia 2-3**: CLI básica (generate-seed, generate, recover)
3. **Dia 4-5**: Test vectors e validação

**MVP Entregue!** 🎉

---

## Conclusão

A implementação de SLIP-39 no secreon é **viável e valiosa**. Apesar da complexidade técnica (GF(256), RS1024, Feistel cipher), seguir a especificação rigorosamente e usar a implementação de referência como guia torna o projeto gerenciável.

**Principais Benefícios**:
- Interoperabilidade com ecossistema cripto moderno
- UX superior (mnemonics vs números grandes)
- Segurança reforçada (checksum + digest + criptografia)
- Flexibilidade (esquema de dois níveis)

**Principais Desafios**:
- Complexidade da especificação (muitos detalhes)
- Garantir compatibilidade 100%
- Evitar bugs criptográficos

**Estratégia de Sucesso**:
- Implementação incremental e testada
- Validação contínua (test vectors + cross-implementation)
- Foco em qualidade e segurança
- Documentação clara

Com o plano de implementação detalhado fornecido, uma equipe ou desenvolvedor experiente pode entregar um MVP funcional em 2-3 semanas e uma implementação completa em 5-6 semanas de trabalho dedicado.

---

**Última Atualização**: 2025-12-06  
**Autor**: AI Assistant (Claude Sonnet 4.5)  
**Status**: READY FOR REVIEW AND DEVELOPMENT

