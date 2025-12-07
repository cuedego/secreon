# Secreon Documentation

Este diretório contém a documentação completa do projeto secreon.

## 📚 Índice de Documentos

### Documentação Geral
- **TECHNICAL.md** - Documentação técnica do secreon atual (SSS clássico)
- **share_schema.json** - Schema JSON para formato de shares

### Documentação SLIP-39 (Nova Feature)

A documentação para implementação de suporte a SLIP-39 está organizada em 4 documentos complementares:

#### 1. SLIP39_SUMMARY.md 🎯
**Propósito**: Resumo executivo e visão geral  
**Público-alvo**: Todos (stakeholders, desenvolvedores, usuários)  
**Conteúdo**:
- Overview da feature
- Comparação SSS clássico vs SLIP-39
- Casos de uso práticos
- Timeline e estimativas
- Próximos passos

**📖 Leia primeiro se você quer**: Entender rapidamente o que é SLIP-39 e por que implementá-lo

---

#### 2. SLIP39_REQUIREMENTS.md 📋
**Propósito**: Especificação completa de requisitos  
**Público-alvo**: Desenvolvedores, arquitetos, QA  
**Conteúdo**:
- Requisitos funcionais (FR-1 a FR-10)
- Requisitos não-funcionais (NFR-1 a NFR-4)
- Arquitetura de módulos
- Critérios de aceite
- Test vectors
- Glossário e referências

**📖 Leia se você precisa**: Entender TODOS os requisitos em detalhes para implementação

---

#### 3. SLIP39_IMPLEMENTATION_PLAN.md 📅
**Propósito**: Plano de desenvolvimento em etapas  
**Público-alvo**: Desenvolvedores, gerentes de projeto  
**Conteúdo**:
- 5 fases de desenvolvimento
- Etapas detalhadas com tarefas, entregáveis e critérios
- Estimativas de tempo
- Priorização (MVP vs feature completa)
- Riscos e mitigações
- Checkpoints de validação

**📖 Leia se você vai**: Implementar a feature e precisa de um roadmap detalhado

---

#### 4. SLIP39_UNDERSTANDING.md 🧠
**Propósito**: Análise técnica profunda e justificativas  
**Público-alvo**: Desenvolvedores experientes, arquitetos  
**Conteúdo**:
- Contexto técnico detalhado
- Diferenças fundamentais SSS clássico vs SLIP-39
- Desafios técnicos e soluções
- Arquitetura proposta
- Estratégia de implementação
- Análise de riscos

**📖 Leia se você quer**: Entendimento profundo da arquitetura e decisões técnicas

---

## 🎯 Como Usar Esta Documentação

### Para Stakeholders / Product Owners:
1. ✅ Comece com **SLIP39_SUMMARY.md**
2. ⏭️ Revise casos de uso e timeline
3. ⏭️ Aprove ou sugira ajustes

### Para Gerentes de Projeto:
1. ✅ Leia **SLIP39_SUMMARY.md** (contexto)
2. ✅ Estude **SLIP39_IMPLEMENTATION_PLAN.md** (planejamento)
3. ⏭️ Use estimativas para planejamento de sprint/release

### Para Desenvolvedores (Implementação):
1. ✅ Leia **SLIP39_SUMMARY.md** (overview)
2. ✅ Estude **SLIP39_REQUIREMENTS.md** (requisitos completos)
3. ✅ Siga **SLIP39_IMPLEMENTATION_PLAN.md** (etapas)
4. ✅ Consulte **SLIP39_UNDERSTANDING.md** para dúvidas técnicas

### Para Arquitetos / Tech Leads:
1. ✅ Leia **SLIP39_UNDERSTANDING.md** (análise técnica profunda)
2. ✅ Revise **SLIP39_REQUIREMENTS.md** (requisitos arquiteturais)
3. ⏭️ Valide decisões de design
4. ⏭️ Faça code review guiado pelos requisitos

### Para QA / Testers:
1. ✅ Leia **SLIP39_SUMMARY.md** (contexto)
2. ✅ Foque em **SLIP39_REQUIREMENTS.md** seções:
   - Critérios de aceite
   - Test vectors
   - Casos de uso
3. ⏭️ Crie test plans baseados nos requisitos

### Para LLMs (Agentes de Desenvolvimento):
1. ✅ Contexto inicial: **SLIP39_SUMMARY.md**
2. ✅ Requisitos completos: **SLIP39_REQUIREMENTS.md**
3. ✅ Roadmap: **SLIP39_IMPLEMENTATION_PLAN.md**
4. ✅ Detalhes técnicos: **SLIP39_UNDERSTANDING.md**
5. ⏭️ Seguir ordem das etapas do plano
6. ⏭️ Validar contra requisitos a cada etapa

---

## 🔗 Documentos Relacionados

### Externos (Especificações):
- [SLIP-39 Specification](https://github.com/satoshilabs/slips/blob/master/slip-0039.md) - Especificação oficial
- [BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) - Mnemonic code for HD wallets
- [BIP-32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) - Hierarchical Deterministic Wallets

### Externos (Implementações de Referência):
- [python-shamir-mnemonic](https://github.com/trezor/python-shamir-mnemonic) - Implementação de referência oficial
- [Test Vectors](https://github.com/trezor/python-shamir-mnemonic/blob/master/vectors.json) - Test vectors oficiais

### Internos (Projeto):
- `README.md` - README principal do secreon
- `CHANGELOG.md` - Histórico de mudanças
- `RELEASE_NOTES.md` - Notas de release

---

## 📊 Estrutura da Documentação SLIP-39

```
docs/
├── SLIP39_SUMMARY.md              # 📄 ~350 linhas
│   └── O que? Por quê? Como? (overview executivo)
│
├── SLIP39_REQUIREMENTS.md         # 📄 ~700 linhas
│   └── Requisitos detalhados (FR + NFR + critérios)
│
├── SLIP39_IMPLEMENTATION_PLAN.md  # 📄 ~800 linhas
│   └── Plano de desenvolvimento em 5 fases + etapas
│
└── SLIP39_UNDERSTANDING.md        # 📄 ~650 linhas
    └── Análise técnica profunda + arquitetura
```

**Total**: ~2500 linhas de documentação completa e estruturada

---

## 🎓 Conceitos-Chave

### SLIP-39
Padrão para backup de wallets cripto usando Shamir's Secret Sharing com mnemonics human-readable.

### Shamir's Secret Sharing (SSS)
Esquema criptográfico para dividir um secret em N shares, onde qualquer T shares podem reconstruir o secret original.

### BIP-39
Padrão para representar entropy como mnemonic de 12-24 palavras.

### Master Secret
O secret original a ser protegido (128-256 bits). Em contexto de wallets cripto, é o BIP-32 master seed.

### Encrypted Master Secret (EMS)
Master secret após criptografia com Feistel cipher e PBKDF2.

### GF(256)
Galois Field com 256 elementos, usado para aritmética em SLIP-39.

### RS1024
Reed-Solomon code sobre GF(1024) usado para checksum forte.

---

## ✅ Status da Documentação

- ✅ **SLIP39_SUMMARY.md** - Completo
- ✅ **SLIP39_REQUIREMENTS.md** - Completo
- ✅ **SLIP39_IMPLEMENTATION_PLAN.md** - Completo
- ✅ **SLIP39_UNDERSTANDING.md** - Completo
- ⏭️ Implementação - A fazer
- ⏭️ User documentation final - Após implementação

---

## 🤝 Contribuindo

Esta documentação foi criada como especificação para desenvolvimento da feature SLIP-39. 

Durante a implementação:
1. Mantenha os documentos atualizados se houver mudanças de requisitos
2. Adicione notas de implementação em SLIP39_UNDERSTANDING.md
3. Documente decisões técnicas importantes
4. Atualize status nos checkpoints

---

## 📞 Suporte

Para dúvidas sobre a documentação ou implementação:
- Revise os 4 documentos SLIP-39 (provavelmente está documentado)
- Consulte especificação oficial SLIP-39
- Abra issue no repositório do secreon

---

**Última Atualização**: 2025-12-06  
**Versão da Documentação**: 1.0  
**Status**: READY FOR REVIEW AND DEVELOPMENT

