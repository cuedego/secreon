# Secreon Documentation

This directory contains the complete documentation for the secreon project.

## 📚 Document Index

### General Documentation
- **TECHNICAL.md** - Technical documentation for current secreon (classic SSS)
- **share_schema.json** - JSON schema for share format

### SLIP-39 Documentation (New Feature)

The documentation for SLIP-39 support implementation is organized into 4 complementary documents:

#### 1. SLIP39_SUMMARY.md 🎯
**Purpose**: Executive summary and overview  
**Target audience**: Everyone (stakeholders, developers, users)  
**Content**:
- Feature overview
- Classic SSS vs SLIP-39 comparison
- Practical use cases
- Timeline and estimates
- Next steps

**📖 Read this first if you want to**: Quickly understand what SLIP-39 is and why implement it

---

#### 2. SLIP39_REQUIREMENTS.md 📋
**Purpose**: Complete requirements specification  
**Target audience**: Developers, architects, QA  
**Content**:
- Functional requirements (FR-1 to FR-10)
- Non-functional requirements (NFR-1 to NFR-4)
- Module architecture
- Acceptance criteria
- Test vectors
- Glossary and references

**📖 Read if you need to**: Understand ALL requirements in detail for implementation

---

#### 3. SLIP39_IMPLEMENTATION_PLAN.md 📅
**Purpose**: Step-by-step development plan  
**Target audience**: Developers, project managers  
**Content**:
- 5 development phases
- Detailed steps with tasks, deliverables, and criteria
- Time estimates
- Prioritization (MVP vs complete feature)
- Risks and mitigations
- Validation checkpoints

**📖 Read if you're going to**: Implement the feature and need a detailed roadmap

---

#### 4. SLIP39_UNDERSTANDING.md 🧠
**Purpose**: Deep technical analysis and rationale  
**Target audience**: Experienced developers, architects  
**Content**:
- Detailed technical context
- Fundamental differences: classic SSS vs SLIP-39
- Technical challenges and solutions
- Proposed architecture
- Implementation strategy
- Risk analysis

**📖 Read if you want**: Deep understanding of architecture and technical decisions

---

## 🎯 How to Use This Documentation

### For Stakeholders / Product Owners:
1. ✅ Start with **SLIP39_SUMMARY.md**
2. ⏭️ Review use cases and timeline
3. ⏭️ Approve or suggest adjustments

### For Project Managers:
1. ✅ Read **SLIP39_SUMMARY.md** (context)
2. ✅ Study **SLIP39_IMPLEMENTATION_PLAN.md** (planning)
3. ⏭️ Use estimates for sprint/release planning

### For Developers (Implementation):
1. ✅ Read **SLIP39_SUMMARY.md** (overview)
2. ✅ Study **SLIP39_REQUIREMENTS.md** (complete requirements)
3. ✅ Follow **SLIP39_IMPLEMENTATION_PLAN.md** (steps)
4. ✅ Consult **SLIP39_UNDERSTANDING.md** for technical questions

### For Architects / Tech Leads:
1. ✅ Read **SLIP39_UNDERSTANDING.md** (deep technical analysis)
2. ✅ Review **SLIP39_REQUIREMENTS.md** (architectural requirements)
3. ⏭️ Validate design decisions
4. ⏭️ Conduct code review guided by requirements

### For QA / Testers:
1. ✅ Read **SLIP39_SUMMARY.md** (context)
2. ✅ Focus on **SLIP39_REQUIREMENTS.md** sections:
   - Acceptance criteria
   - Test vectors
   - Use cases
3. ⏭️ Create test plans based on requirements

### For LLMs (Development Agents):
1. ✅ Initial context: **SLIP39_SUMMARY.md**
2. ✅ Complete requirements: **SLIP39_REQUIREMENTS.md**
3. ✅ Roadmap: **SLIP39_IMPLEMENTATION_PLAN.md**
4. ✅ Technical details: **SLIP39_UNDERSTANDING.md**
5. ⏭️ Follow plan step order
6. ⏭️ Validate against requirements at each step

---

## 🔗 Related Documents

### External (Specifications):
- [SLIP-39 Specification](https://github.com/satoshilabs/slips/blob/master/slip-0039.md) - Especificação oficial
- [BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) - Mnemonic code for HD wallets
- [BIP-32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) - Hierarchical Deterministic Wallets

### External (Reference Implementations):
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
├── SLIP39_SUMMARY.md              # 📄 ~350 lines
│   └── What? Why? How? (executive overview)
│
├── SLIP39_REQUIREMENTS.md         # 📄 ~700 lines
│   └── Detailed requirements (FR + NFR + criteria)
│
├── SLIP39_IMPLEMENTATION_PLAN.md  # 📄 ~800 lines
│   └── Development plan in 5 phases + steps
│
└── SLIP39_UNDERSTANDING.md        # 📄 ~650 lines
    └── Deep technical analysis + architecture
```

**Total**: ~2500 lines of complete and structured documentation

---

## 🎓 Key Concepts

### SLIP-39
Standard for crypto wallet backup using Shamir's Secret Sharing with human-readable mnemonics.

### Shamir's Secret Sharing (SSS)
Cryptographic scheme to split a secret into N shares, where any T shares can reconstruct the original secret.

### BIP-39
Standard for representing entropy as 12-24 word mnemonics.

### Master Secret
The original secret to be protected (128-256 bits). In crypto wallet context, it's the BIP-32 master seed.

### Encrypted Master Secret (EMS)
Master secret after encryption with Feistel cipher and PBKDF2.

### GF(256)
Galois Field with 256 elements, used for arithmetic in SLIP-39.

### RS1024
Reed-Solomon code over GF(1024) used for strong checksum.

---

## ✅ Documentation Status

- ✅ **SLIP39_SUMMARY.md** - Complete
- ✅ **SLIP39_REQUIREMENTS.md** - Complete
- ✅ **SLIP39_IMPLEMENTATION_PLAN.md** - Complete
- ✅ **SLIP39_UNDERSTANDING.md** - Complete
- ⏭️ Implementation - To do
- ⏭️ Final user documentation - After implementation

---

## 🤝 Contributing

This documentation was created as specification for SLIP-39 feature development. 

During implementation:
1. Keep documents updated if requirements change
2. Add implementation notes to SLIP39_UNDERSTANDING.md
3. Document important technical decisions
4. Update status at checkpoints

---

## 📞 Support

For questions about documentation or implementation:
- Review the 4 SLIP-39 documents (probably documented there)
- Consult official SLIP-39 specification
- Open issue in secreon repository

---

**Last Updated**: 2025-12-07  
**Documentation Version**: 1.0  
**Status**: READY FOR REVIEW AND DEVELOPMENT

