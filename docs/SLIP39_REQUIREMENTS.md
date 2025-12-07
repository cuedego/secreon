# SLIP-39 Support - Requirements Document

## Executive Summary

Este documento define os requisitos para implementar suporte a SLIP-39 (Shamir's Secret-Sharing for Mnemonic Codes) no secreon, permitindo:
1. Geração de seed phrases de 24 palavras (master secret)
2. Divisão de secrets em shares usando mnemonics SLIP-39
3. Recuperação de secrets a partir de mnemonics SLIP-39

## Context and Background

### Current State (Secreon v1)
O secreon atualmente implementa:
- Shamir's Secret Sharing (SSS) clássico usando aritmética sobre campo primo (2^2203-1)
- Conversão de secrets (strings/arquivos) para inteiros
- Geração de shares como pares (x, y)
- Serialização em JSON
- Suporte a KDF (SHA-256, PBKDF2) para passphrases

### SLIP-39 Overview
SLIP-39 é um padrão para backup de wallets hierárquicas determinísticas (BIP-32) usando SSS, definido em:
- Especificação: https://github.com/satoshilabs/slips/blob/master/slip-0039.md
- Implementação de referência: https://github.com/trezor/python-shamir-mnemonic

**Características principais:**
- Mnemonics de 20-33 palavras (dependendo do tamanho do master secret)
- Wordlist fixa de 1024 palavras
- Esquema de dois níveis: grupos (GT-of-G) e membros (Ti-of-Ni)
- Checksum RS1024 (Reed-Solomon)
- Criptografia do master secret com PBKDF2/Feistel network
- Suporte a passphrase opcional
- GF(256) para aritmética (ao invés de campo primo grande)

## Requirements

### FR-1: BIP-39 Seed Phrase Generation
**Priority: HIGH**

#### FR-1.1: Generate 24-word BIP-39 Mnemonic
- O secreon deve ser capaz de gerar uma seed phrase BIP-39 de 24 palavras
- Entropia: 256 bits (32 bytes)
- Wordlist: BIP-39 English (2048 palavras)
- Formato: 24 palavras separadas por espaços
- Checksum: 8 bits (SHA-256 dos primeiros 32 bytes)

#### FR-1.2: BIP-39 to Master Secret Conversion
- Converter BIP-39 mnemonic para master secret (entropy)
- Master secret = primeiros 32 bytes da entropia original
- Validar checksum da mnemonic BIP-39
- Suportar importação de mnemonics existentes

**Nota importante:** Para compatibilidade com wallets, o master secret usado em SLIP-39 deve ser o **BIP-32 master seed** (não o seed derivado via PBKDF2 do BIP-39).

### FR-2: SLIP-39 Share Generation
**Priority: HIGH**

#### FR-2.1: Generate SLIP-39 Shares from Master Secret
- Input: master secret (128-256 bits, múltiplo de 16 bits)
- Output: conjunto de mnemonics SLIP-39
- Suportar esquema de nível único (1 grupo) para casos simples
- Suportar esquema de dois níveis (múltiplos grupos) para casos avançados

#### FR-2.2: Single-Level Scheme (T-of-N)
- Permitir criar shares com threshold T e total N
- Validações:
  - 1 ≤ T ≤ N ≤ 16
  - Comprimento do master secret ≥ 128 bits e múltiplo de 16 bits
- Implementação recomendada: 1 grupo com T1=T e N1=N

#### FR-2.3: Two-Level Scheme (GT-of-G with Ti-of-Ni)
- Group threshold (GT): número de grupos necessários para recuperação
- Por grupo i: member threshold (Ti) e member count (Ni)
- Validações:
  - 1 ≤ GT ≤ G ≤ 16
  - Para cada grupo: 1 ≤ Ti ≤ Ni ≤ 16
  - Se Ti = 1, então Ni DEVE ser 1 (evitar 1-of-N com N > 1)

#### FR-2.4: SLIP-39 Mnemonic Format
- Cada share é codificado como mnemonic de 20-33 palavras
- Estrutura (bits):
  - Identifier (15): identificador aleatório comum a todas as shares
  - Extendable flag (1): flag de backup extensível
  - Iteration exponent (4): expoente para PBKDF2 (10000×2^e iterações)
  - Group index (4): índice do grupo
  - Group threshold (4): GT-1
  - Group count (4): G-1
  - Member index (4): índice do membro no grupo
  - Member threshold (4): Ti-1
  - Share value (variável): valor do share com padding
  - Checksum (30): RS1024 checksum
- Wordlist: SLIP-39 wordlist de 1024 palavras
- Encoding: cada 10 bits = 1 palavra

### FR-3: SLIP-39 Share Recovery
**Priority: HIGH**

#### FR-3.1: Recover Master Secret from SLIP-39 Mnemonics
- Input: conjunto de mnemonics SLIP-39 + passphrase opcional
- Output: master secret original
- Validar todas as shares pertencem ao mesmo backup (mesmo identifier)
- Validar número suficiente de grupos e membros
- Verificar checksum de cada mnemonic

#### FR-3.2: Incremental Share Collection
- Permitir adicionar shares incrementalmente
- Informar quantas shares/grupos ainda faltam
- Detectar shares inválidas ou incompatíveis

### FR-4: Encryption and Security
**Priority: HIGH**

#### FR-4.1: Master Secret Encryption
- Usar Feistel cipher de 4 rounds com PBKDF2 como função de round
- PBKDF2 parâmetros:
  - PRF: HMAC-SHA256
  - Password: (round_number || passphrase)
  - Salt: ("shamir" || identifier) || R (quando ext=0) ou apenas R (quando ext=1)
  - Iterations: 2500 × 2^e (onde e = iteration exponent)
  - dkLen: n/2 bytes (metade do tamanho do master secret)

#### FR-4.2: Passphrase Support
- Passphrase opcional (ASCII imprimível, caracteres 32-126)
- Passphrase vazia por padrão
- Não há verificação de passphrase correta (plausible deniability)

#### FR-4.3: Digest Verification
- Para threshold ≥ 2, incluir digest do shared secret
- Digest = primeiros 4 bytes de HMAC-SHA256(key=R, msg=S)
- Permite detectar shares maliciosas ou incorretas

### FR-5: GF(256) Arithmetic
**Priority: HIGH**

#### FR-5.1: Galois Field Operations
- Implementar GF(256) usando representação polinomial
- Polinômio irredutível: x^8 + x^4 + x^3 + x + 1 (Rijndael)
- Operações: adição (XOR), multiplicação, divisão (inverso multiplicativo)
- Pré-computar tabelas de log/exp para eficiência

#### FR-5.2: Secret Splitting on GF(256)
- Aplicar SSS byte-a-byte sobre o secret
- Para cada byte, criar polinômio de grau (threshold-1)
- Secret armazenado em x=255
- Digest armazenado em x=254 (quando threshold ≥ 2)

### FR-6: Checksum and Validation
**Priority: HIGH**

#### FR-6.1: RS1024 Checksum
- Implementar Reed-Solomon code sobre GF(1024)
- Polinômio gerador: (x-a)(x-a²)(x-a³) onde a é raiz de x^10 + x^3 + 1
- Comprimento: 3 palavras (30 bits)
- Customization strings:
  - "shamir" quando ext=0
  - "shamir_extendable" quando ext=1

#### FR-6.2: Mnemonic Validation
- Validar checksum de cada mnemonic
- Validar comprimento mínimo (20 palavras)
- Validar padding bits (devem ser zeros e ≤ 8 bits)
- Validar consistência de parâmetros entre shares

### FR-7: User Interface and CLI
**Priority: MEDIUM**

#### FR-7.1: Generate Command Extensions
```bash
# Gerar BIP-39 seed (24 palavras)
secreon slip39 generate-seed --out seed.txt

# Gerar SLIP-39 shares de uma BIP-39 seed
secreon slip39 generate --seed-file seed.txt --threshold 3 --shares 5 --out shares/

# Gerar SLIP-39 shares de um master secret hex
secreon slip39 generate --master-secret <hex> --threshold 3 --shares 5 --out shares/

# Esquema avançado (2 grupos)
secreon slip39 generate --master-secret <hex> \
  --group-threshold 2 \
  --group 2 3 \
  --group 3 5 \
  --out shares/

# Com passphrase
secreon slip39 generate --seed-file seed.txt --threshold 3 --shares 5 \
  --passphrase "my secure passphrase" --out shares/
```

#### FR-7.2: Recover Command
```bash
# Recuperar de mnemonics
secreon slip39 recover --mnemonics mnemonic1.txt mnemonic2.txt mnemonic3.txt

# Recuperar de diretório
secreon slip39 recover --shares-dir shares/ --passphrase "my secure passphrase"

# Recuperar interativamente
secreon slip39 recover --interactive
```

#### FR-7.3: Display Formats
- Exibir shares como mnemonics (palavras)
- Suportar exportação em JSON para compatibilidade
- Exibir informações sobre shares (grupo, threshold, etc.)
- Warnings claros sobre distribuição segura de shares

### FR-8: Compatibility and Interoperability
**Priority: HIGH**

#### FR-8.1: SLIP-39 Standard Compliance
- Implementação 100% compatível com especificação SLIP-39
- Passar todos os test vectors oficiais
- Interoperável com Trezor, Ledger, e outras implementações

#### FR-8.2: Wordlist Management
- Incluir SLIP-39 wordlist oficial
- Suportar validação de palavras
- Suporte a prefixos únicos de 4 letras

#### FR-8.3: BIP-39 Compatibility
- Incluir BIP-39 wordlist (English)
- Suportar conversão bidirecional entre BIP-39 e entropy
- **Importante:** SLIP-39 e BIP-39 não são diretamente conversíveis
  - SLIP-39 usa master seed (entropy)
  - BIP-39 usa seed derivado via PBKDF2

### FR-9: Testing and Quality
**Priority: HIGH**

#### FR-9.1: Unit Tests
- Testes para todas as operações de GF(256)
- Testes de criptografia/descriptografia
- Testes de geração e recuperação de shares
- Testes de validação e checksum

#### FR-9.2: Integration Tests
- Test vectors oficiais do SLIP-39
- Testes de interoperabilidade com python-shamir-mnemonic
- Testes de casos extremos (threshold=1, shares máximos, etc.)

#### FR-9.3: Property-Based Tests
- Qualquer conjunto válido de T shares recupera o secret
- Menos de T shares não vaza informação
- Shares de grupos diferentes não funcionam sozinhas

### FR-10: Documentation
**Priority: MEDIUM**

#### FR-10.1: User Documentation
- Tutorial passo-a-passo para criar backup
- Exemplos de casos de uso (pessoal, família, empresarial)
- Best practices para distribuição de shares
- Explicação de segurança e trade-offs

#### FR-10.2: Technical Documentation
- Documentação da arquitetura
- API reference
- Algoritmos e estruturas de dados
- Diferenças entre SSS clássico e SLIP-39

## Non-Functional Requirements

### NFR-1: Performance
- Geração de shares: < 5 segundos para master secret de 256 bits
- Recuperação de shares: < 10 segundos (devido ao PBKDF2)
- Tempo dominado por PBKDF2 (10000+ iterações)

### NFR-2: Security
- Usar fonte criptograficamente segura de aleatoriedade (`secrets` module)
- Nunca logar ou exibir master secret sem confirmação explícita
- Warnings sobre distribuição segura de shares
- Suporte a memory zeroing onde possível (Python limitation)

### NFR-3: Usability
- Interface CLI clara e intuitiva
- Mensagens de erro descritivas
- Validação de entrada antes de operações custosas
- Suporte a operações batch

### NFR-4: Maintainability
- Código modular e bem organizado
- Type hints completos
- Testes com boa cobertura (>80%)
- Documentação inline

## Technical Architecture

### Module Structure
```
secreon/
├── src/
│   ├── sss.py              # Existing SSS implementation
│   ├── slip39/
│   │   ├── __init__.py
│   │   ├── wordlist.py     # SLIP-39 wordlist
│   │   ├── bip39.py        # BIP-39 wordlist and operations
│   │   ├── gf256.py        # GF(256) arithmetic
│   │   ├── rs1024.py       # RS1024 checksum
│   │   ├── cipher.py       # Feistel cipher / encryption
│   │   ├── share.py        # Share class and encoding/decoding
│   │   ├── shamir.py       # SLIP-39 SSS implementation
│   │   └── cli.py          # CLI commands for SLIP-39
│   └── ...
├── tests/
│   ├── test_sss.py         # Existing tests
│   ├── slip39/
│   │   ├── test_gf256.py
│   │   ├── test_rs1024.py
│   │   ├── test_cipher.py
│   │   ├── test_shamir.py
│   │   └── test_vectors.py # Official SLIP-39 test vectors
│   └── ...
└── ...
```

### Dependencies
- **No external dependencies** para funcionalidade core (apenas stdlib)
- Opcional: `click` para CLI avançada (já usado em python-shamir-mnemonic)
- Para testes: `pytest`, `hypothesis` (property-based testing)

## Migration and Compatibility

### Backward Compatibility
- Secreon existente continua funcionando sem mudanças
- SLIP-39 é adicionado como novo subcomando
- Formato JSON de shares clássicas permanece inalterado

### Forward Compatibility
- Implementar ext=1 (extendable backup flag) por padrão
- Suportar versões futuras do SLIP-39 via ext flag

## Risk Assessment

### High Risk Items
1. **Complexidade da especificação SLIP-39**: muitos detalhes, fácil errar
   - Mitigação: implementação incremental, test vectors, code review

2. **Interoperabilidade**: incompatibilidade com outras implementações
   - Mitigação: testes cruzados com python-shamir-mnemonic, Trezor

3. **Segurança criptográfica**: bugs podem comprometer secrets
   - Mitigação: auditoria de código, testes extensivos, usar implementação de referência como guia

### Medium Risk Items
1. **Performance de PBKDF2**: pode ser lento em hardware limitado
   - Mitigação: permitir configuração de iteration exponent

2. **UX complexa**: esquema de dois níveis pode confundir usuários
   - Mitigação: documentação clara, exemplos, modo simples por padrão

## Success Criteria

### Minimum Viable Product (MVP)
1. ✅ Geração de BIP-39 seed de 24 palavras
2. ✅ Conversão BIP-39 → master secret
3. ✅ Geração de SLIP-39 shares (esquema de nível único)
4. ✅ Recuperação de master secret de SLIP-39 shares
5. ✅ Passar test vectors oficiais básicos
6. ✅ CLI funcional para operações básicas

### Full Feature Set
1. ✅ Suporte a esquema de dois níveis (grupos)
2. ✅ Suporte a passphrase
3. ✅ Configuração de iteration exponent
4. ✅ Extendable backup flag
5. ✅ Interoperabilidade completa com outras implementações
6. ✅ Documentação completa
7. ✅ Cobertura de testes >80%

## References

1. **SLIP-39 Specification**: https://github.com/satoshilabs/slips/blob/master/slip-0039.md
2. **Reference Implementation**: https://github.com/trezor/python-shamir-mnemonic
3. **BIP-39**: https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
4. **BIP-32**: https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
5. **Test Vectors**: https://github.com/trezor/python-shamir-mnemonic/blob/master/vectors.json
6. **SLIP-39 Wordlist**: https://github.com/satoshilabs/slips/blob/master/slip-0039/wordlist.txt

## Glossary

- **Master Secret (MS)**: O secret original a ser protegido (128-256 bits)
- **Encrypted Master Secret (EMS)**: Master secret após criptografia com Feistel cipher
- **Share**: Um único ponto (x, y) no esquema SSS
- **Mnemonic**: Representação de um share como palavras
- **Group**: Conjunto de member shares no esquema de dois níveis
- **Threshold**: Número mínimo de shares necessárias para recuperação
- **GF(256)**: Galois Field com 256 elementos, usado para aritmética
- **RS1024**: Reed-Solomon code sobre GF(1024) para checksum
- **Identifier**: ID aleatório de 15 bits comum a todas as shares de um backup

## Appendix A: Example Scenarios

### Scenario 1: Personal Backup (Simple)
**Goal**: Proteger uma wallet pessoal com redundância

**Setup**:
- Generate 24-word BIP-39 seed
- Create 3-of-5 SLIP-39 shares
- Store: 1 em casa, 1 no trabalho, 1 cofre, 2 com amigos

**Commands**:
```bash
secreon slip39 generate-seed --out seed.txt
secreon slip39 generate --seed-file seed.txt --threshold 3 --shares 5 --out shares/
```

### Scenario 2: Family Backup (Two-Level)
**Goal**: Você pode recuperar sozinho OU sua família pode recuperar juntos

**Setup**:
- Group 1: 2-of-2 (seus shares pessoais)
- Group 2: 3-of-5 (shares da família)
- Group threshold: 1 (qualquer grupo completo)

**Commands**:
```bash
secreon slip39 generate --seed-file seed.txt \
  --group-threshold 1 \
  --group 2 2 \
  --group 3 5 \
  --out shares/
```

### Scenario 3: Corporate Backup (Advanced)
**Goal**: Requer aprovação de múltiplos departamentos

**Setup**:
- Group 1: 2-of-3 (diretores)
- Group 2: 3-of-5 (equipe técnica)
- Group 3: 2-of-3 (compliance)
- Group threshold: 2 (dois departamentos devem concordar)

**Commands**:
```bash
secreon slip39 generate --master-secret <hex> \
  --group-threshold 2 \
  --group 2 3 \
  --group 3 5 \
  --group 2 3 \
  --out shares/
```

## Appendix B: Migration Path from Legacy SSS

Para usuários existentes do secreon que usam SSS clássico:

1. **Não há conversão direta**: SSS clássico e SLIP-39 são incompatíveis
2. **Recomendação**: 
   - Recuperar o secret original usando shares antigas
   - Gerar novas shares SLIP-39 do secret
   - Destruir shares antigas de forma segura
3. **Coexistência**: ambos os sistemas podem coexistir no secreon

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-06 | AI Assistant | Initial requirements document |

---
**Document Status**: DRAFT
**Última Atualização**: 2025-12-06

