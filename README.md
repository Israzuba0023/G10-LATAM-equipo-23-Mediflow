# 🏥 MediFlow – Agente Autônomo para Triagem, Extração e Roteamento de Documentos Clínicos

> **Hackathon ONE Grupo 10** | Oracle Next Education & Alura  
> **Repositório:** `G10-LATAM-equipo-23-Mediflow`  
> **Stack:** Python, FastAPI, LangGraph / LLM Agents, Oracle Cloud Infrastructure (OCI), React

---

## 📋 Sobre o Projeto

O **MediFlow** é uma solução inteligente baseada em IA Multimodal, Agentes Autônomos e Arquitetura Defensiva desenvolvida para resolver o gargalo do processamento manual de documentos na área da saúde (*HealthTech* / Gestão Hospitalar).

Diariamente, hospitais e clínicas lidam com milhares de documentos heterogêneos (PDFs digitalizados, imagens de exames/receitas, laudos e guias TISS/TUSS). O MediFlow automatiza a **classificação, extração precisa de dados clínicos**, **anonymização preventiva de dados de saúde** e **roteamento condicional**, reduzindo erros de digitação e acelerando o atendimento aos pacientes com máxima segurança e conformidade normativa (LGPD / HIPAA).

---

## 💡 Principais Funcionalidades

- **Ingestão Multimodal & Sanitizada:** Ingestão segura de arquivos em PDF, Imagem ou payloads JSON com validação de *magic bytes* e MIME types.
- **Camada de Segurança Cognitive (Guardrails Anti-Prompt Injection):** Proteção nativa contra injeções de prompt indiretas em documentos clínicos e tentativas de supressão das instruções do sistema.
- **Anonimização Ativa de Dados Sensíveis (PII / PHI):** Filtro inteligente de privacidade que detecta e descaracteriza identificadores de pacientes antes de interagir com provedores de LLM externos.
- **Classificação & Extração Estruturada:** Identificação automatizada do tipo documental (Receituários, Laudos, Guia TISS/TUSS, Relatórios) com serialização estrita via Pydantic.
- **Grafo de Decisão Condicional:** Decisões dinâmicas de roteamento pautadas pelo score de confiança do extrator e grau de severidade médica.
- **Gestão Crítica de Urgências:** Alerta instantâneo e roteamento prioritário de achados urgentes (ex: Tromboembolismo Pulmonar Agudo) para filas de resposta rápida.
- **Human-in-the-Loop (HitL):** Redirecionamento automático de dados ambíguos ou com baixa confiança para auditoria e revisão médica.
- **Integração com OCI Object Storage:** Armazenamento resiliente e segregado por status (`/recebidos`, `/processados`, `/auditoria_humana`) em infraestrutura Oracle Cloud (Always Free).

---

## 🏗️ Arquitetura e Fluxo da Aplicação

```text
                     +----------------------------------+
                     | Ingestão (PDF / Imagem / JSON)   |
                     +----------------------------------+
                                      |
                                      v
                     +----------------------------------+
                     |  Módulo Defensivo & Segurança    |
                     |  (Guardrails + Desidentificação) |
                     +----------------------------------+
                                      |
                                      v
                     +----------------------------------+
                     |   IA Multimodal (LLM / Vision)   |
                     |  Classificação + Extração JSON   |
                     +----------------------------------+
                                      |
                                      v
                     +----------------------------------+
                     | Grafo de Decisão (LangGraph/n8n) |
                     +----------------------------------+
                       /              |                \
                      /               |                 \
                     v                v                  v
           [ Score Confiança OK ] [ Urgência Médica ] [ Ambíguo / Falha ]
                     |                |                  |
                     v                v                  v
            +-----------------+ +---------------+ +------------------+
            |  Fila Padrão /  | |   Alerta de   | |   Auditoria      |
            |  Sistema PEP    | |  Plantão/UTI  | |   Humana (HitL)  |
            +-----------------+ +---------------+ +------------------+
                     \                |                /
                      +---------------+---------------+
                                      |
                                      v
                     +----------------------------------+
                     | Integration: OCI Object Storage  |
                     |     (Camada Always Free)         |
                     +----------------------------------+
```

---

## 🔒 Diretrizes de Segurança & Conformidade

O MediFlow adota o princípio de **Defesa em Profundidade** para garantir o tratamento seguro de dados de saúde:

1. **Gestão Segura de Variáveis de Ambiente:** Nenhuma chave de API ou credencial deve ser persistida nos arquivos de código ou versionada no repositório. O uso do arquivo `.env` é exclusivamente local e mantido no `.gitignore`.
2. **Proteção Anti-Prompt Injection:** O fluxo de entrada do agente sanitiza textos extraídos de OCR/PDFs para prevenir execução maliciosa de instruções (*Indirect Prompt Injection*).
3. **Privacidade por Design (LGPD/HIPAA):** Dados sensíveis de identificação do paciente (PII) e informações de saúde (PHI) são anonimizados antes do envio para modelos externos.
4. **Validação Rígida de Esquemas:** Todas as respostas geradas pela LLM passam por validação Pydantic. Retornos mal formatados ou fora de conformidade acionam automaticamente a fila de auditoria (HitL).

---

## 📂 Estrutura Modular do Projeto

```text
G10-LATAM-equipo-23-Mediflow/
├── .env.example                # Modelo de variáveis de ambiente (sem segredos)
├── .gitignore                  # Bloqueio de arquivos sensíveis e temporários
├── README.md                   # Documentação oficial da aplicação
├── requirements.txt            # Dependências da aplicação com versões fixadas
│
├── backend/                    # API FastAPI e Agentes de IA
│   ├── app/
│   │   ├── main.py             # Instância FastAPI, middlewares (CORS, Rate Limit)
│   │   ├── api/                # Endpoints REST (Triagem, Roteamento, Status)
│   │   ├── agent/              # Orquestração da LLM e grafos de decisão
│   │   ├── security/           # Defesa (Guardrails, Anonimizador PII, File Checker)
│   │   └── schemas/            # Contratos de dados e validações Pydantic
│   └── tests/                  # Suíte de testes unitários e de segurança
│
└── frontend/                   # Interface da Aplicação Web
    ├── public/
    └── src/
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
* Python 3.10+
* Node.js 18+ (para execução do Frontend)
* Conta na Oracle Cloud Infrastructure (OCI) ou chaves de API configuradas

### 1. Configuração do Backend
```bash
# Clone o repositório
git clone https://github.com/Hackathon-ONE-G10/G10-LATAM-equipo-23-Mediflow.git
cd G10-LATAM-equipo-23-Mediflow

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Preencha as chaves no arquivo .env

# Execute o servidor FastAPI
cd backend
uvicorn app.main:app --reload
```

---

## 🛡️ Licença e Responsabilidade

Desenvolvido pelo **Grupo 23** durante a **Hackathon ONE Grupo 10 (Oracle Next Education & Alura)**.  
Este projeto destina-se ao auxílio do fluxo de triagem hospitalar e suporte à decisão, respeitando a supervisão médica (*Human-in-the-Loop*).
