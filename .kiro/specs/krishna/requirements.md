# KRISHNA - AI Personal Tutor System Requirements

## Project Overview

KRISHNA is a multi-agent AI personal tutor system designed to facilitate learning from large documents such as textbooks, PDFs, and research papers. The system employs advanced machine learning techniques including Recursive Language Models (RLMs) for hierarchical document understanding, Energy-Based Models (EBMs) for concept validation and prerequisite enforcement, and attention-efficient inference strategies for resource-constrained local execution.

The system autonomously ingests complex documents, extracts conceptual knowledge, generates personalized curricula, and provides adaptive teaching through interactive lessons and assessments. KRISHNA tracks learner progress, identifies knowledge gaps, and dynamically adjusts instruction to reinforce weak concepts and correct misconceptions.

## Problem Statement

Traditional learning from large documents presents several challenges:

- **Context Limitations**: Standard language models cannot process documents exceeding their context window, limiting comprehension of lengthy textbooks and research papers
- **Passive Learning**: Learners struggle to extract structured knowledge from unstructured documents without guidance
- **Lack of Personalization**: Static content cannot adapt to individual learner needs, pace, or knowledge gaps
- **Prerequisite Gaps**: Learners often encounter advanced concepts without mastering foundational prerequisites
- **Resource Constraints**: Existing AI tutoring solutions require expensive cloud infrastructure or high-end hardware
- **Privacy Concerns**: Cloud-based systems expose sensitive learning data and personal information
- **Incomplete Information**: Single documents may lack sufficient context or explanations for complex topics

KRISHNA addresses these challenges by providing an intelligent, adaptive, privacy-preserving tutoring system that can operate locally while maintaining sophisticated reasoning capabilities.

## Objectives

### Primary Objectives

- Enable effective learning from documents exceeding standard LLM context limits through recursive decomposition and understanding
- Provide personalized, adaptive instruction that responds to individual learner performance and knowledge gaps
- Ensure local-first execution on resource-constrained hardware while maintaining teaching quality
- Detect and remediate misconceptions and weak concepts through continuous assessment
- Generate coherent curricula that respect prerequisite relationships and conceptual dependencies

### Secondary Objectives

- Minimize operational costs through efficient inference and local execution
- Protect learner privacy by avoiding unnecessary data transmission
- Augment document-based knowledge with external sources when needed
- Provide explainable teaching decisions and learning recommendations
- Support extensibility for future teaching strategies and agent capabilities

## Functional Requirements

### FR1: Document Ingestion and Processing

- **FR1.1**: The system shall accept documents in multiple formats including PDF, plain text, Markdown, and common document formats
- **FR1.2**: The system shall handle documents exceeding standard LLM context limits (>100,000 tokens)
- **FR1.3**: The system shall decompose large documents into hierarchical chunks using Recursive Language Model (RLM) style processing
- **FR1.4**: The system shall preserve document structure including sections, subsections, figures, tables, and references during ingestion
- **FR1.5**: The system shall extract and index key concepts, definitions, theorems, and examples from ingested documents

### FR2: Concept Extraction and Knowledge Graph Construction

- **FR2.1**: The system shall automatically identify core concepts, topics, and subtopics from document content
- **FR2.2**: The system shall construct a directed acyclic graph (DAG) representing concept dependencies and prerequisites
- **FR2.3**: The system shall assign difficulty levels and estimated learning time to each concept
- **FR2.4**: The system shall identify relationships between concepts including "prerequisite", "related", and "extends"
- **FR2.5**: The system shall validate concept graphs using Energy-Based Model (EBM) constraints to ensure logical prerequisite ordering

### FR3: Multi-Agent Orchestration

- **FR3.1**: The system shall implement distinct specialized agents with clearly defined responsibilities
- **FR3.2**: The system shall include at minimum: Document Understanding Agent, Curriculum Planning Agent, Teaching Agent, Assessment Agent, and Progress Tracking Agent
- **FR3.3**: The system shall coordinate agent interactions through a central orchestration mechanism
- **FR3.4**: The system shall enable agents to communicate through structured message passing
- **FR3.5**: The system shall support dynamic agent invocation based on learner needs and system state

### FR4: Curriculum Generation and Planning

- **FR4.1**: The system shall generate personalized learning curricula from unstructured document content
- **FR4.2**: The system shall order curriculum topics according to prerequisite dependencies
- **FR4.3**: The system shall estimate time requirements for each curriculum unit
- **FR4.4**: The system shall adapt curriculum pacing based on learner performance
- **FR4.5**: The system shall support curriculum branching for remediation and advanced topics

### FR5: Adaptive Teaching Behavior

- **FR5.1**: The system shall deliver interactive lessons explaining concepts from the curriculum
- **FR5.2**: The system shall adjust explanation depth and complexity based on learner responses
- **FR5.3**: The system shall provide examples, analogies, and visualizations to support understanding
- **FR5.4**: The system shall respond to learner questions and requests for clarification
- **FR5.5**: The system shall use EBM-driven validation to ensure teaching order respects prerequisite constraints

### FR6: Quiz Generation and Evaluation

- **FR6.1**: The system shall automatically generate quizzes aligned with curriculum concepts
- **FR6.2**: The system shall support multiple question types including multiple choice, short answer, and problem-solving
- **FR6.3**: The system shall evaluate learner responses for correctness and understanding
- **FR6.4**: The system shall provide detailed feedback on incorrect answers
- **FR6.5**: The system shall adjust quiz difficulty based on learner performance

### FR7: Learning Progress Tracking

- **FR7.1**: The system shall track time spent on each concept and learning activity
- **FR7.2**: The system shall record quiz scores and accuracy metrics for each concept
- **FR7.3**: The system shall maintain a history of learner interactions and responses
- **FR7.4**: The system shall compute mastery levels for each concept based on performance data
- **FR7.5**: The system shall identify error patterns and common mistakes across concepts

### FR8: Weak Concept and Misconception Detection

- **FR8.1**: The system shall identify concepts with low mastery scores or high error rates
- **FR8.2**: The system shall detect misconceptions through analysis of incorrect responses and reasoning patterns
- **FR8.3**: The system shall classify misconceptions by type and severity
- **FR8.4**: The system shall prioritize weak concepts for remediation based on prerequisite importance
- **FR8.5**: The system shall distinguish between knowledge gaps and conceptual misunderstandings

### FR9: Autonomous Revision and Prerequisite Reinforcement

- **FR9.1**: The system shall automatically trigger revision sessions when weak concepts are detected
- **FR9.2**: The system shall reinforce prerequisite concepts when learners struggle with dependent topics
- **FR9.3**: The system shall validate prerequisite mastery before advancing to dependent concepts using EBM constraints
- **FR9.4**: The system shall generate targeted remediation content addressing specific misconceptions
- **FR9.5**: The system shall track revision effectiveness and adjust strategies accordingly

### FR10: Web Search Augmentation

- **FR10.1**: The system shall detect when document content is insufficient to answer learner questions
- **FR10.2**: The system shall perform autonomous web searches to supplement document knowledge
- **FR10.3**: The system shall evaluate and filter search results for relevance and quality
- **FR10.4**: The system shall integrate external information into teaching responses
- **FR10.5**: The system shall cite sources when using externally retrieved information

### FR11: Local-First Execution

- **FR11.1**: The system shall execute all core functionality on local hardware without requiring cloud services
- **FR11.2**: The system shall support optional cloud-based augmentation for enhanced capabilities
- **FR11.3**: The system shall use attention-efficient or attentionless inference strategies to reduce memory usage
- **FR11.4**: The system shall implement model quantization and optimization for resource-constrained devices
- **FR11.5**: The system shall gracefully degrade functionality when resource limits are reached

## Non-Functional Requirements

### NFR1: Performance and Resource Efficiency

- **NFR1.1**: The system shall run on consumer-grade hardware with 8GB RAM minimum
- **NFR1.2**: The system shall use attention-efficient or attentionless inference mechanisms to minimize memory footprint
- **NFR1.3**: The system shall process document chunks and generate responses within reasonable time bounds (<30 seconds per interaction)
- **NFR1.4**: The system shall support batch processing of documents for offline preparation
- **NFR1.5**: The system shall optimize inference costs to enable large-scale deployment

### NFR2: Privacy and Security

- **NFR2.1**: The system shall minimize data transmission to external services
- **NFR2.2**: The system shall encrypt learner data at rest and in transit
- **NFR2.3**: The system shall provide user control over data sharing and cloud augmentation
- **NFR2.4**: The system shall not store personally identifiable information unnecessarily
- **NFR2.5**: The system shall comply with privacy regulations including GDPR and COPPA where applicable

### NFR3: Modularity and Extensibility

- **NFR3.1**: The system shall implement a modular agent architecture supporting independent agent development
- **NFR3.2**: The system shall provide clear interfaces for adding new agent types
- **NFR3.3**: The system shall support pluggable inference backends and model providers
- **NFR3.4**: The system shall enable configuration of teaching strategies and assessment methods
- **NFR3.5**: The system shall maintain backward compatibility when adding new features

### NFR4: Explainability and Transparency

- **NFR4.1**: The system shall provide explanations for curriculum decisions and topic ordering
- **NFR4.2**: The system shall explain why specific concepts are identified as weak or requiring revision
- **NFR4.3**: The system shall show prerequisite relationships and dependencies to learners
- **NFR4.4**: The system shall log agent decisions and reasoning for debugging and analysis
- **NFR4.5**: The system shall provide visualizations of learning progress and concept mastery

### NFR5: Reliability and Robustness

- **NFR5.1**: The system shall handle malformed or incomplete documents gracefully
- **NFR5.2**: The system shall recover from agent failures without losing learner progress
- **NFR5.3**: The system shall validate all generated content for coherence and accuracy
- **NFR5.4**: The system shall implement error handling and logging throughout the system
- **NFR5.5**: The system shall maintain data consistency across agent interactions

### NFR6: Usability and Accessibility

- **NFR6.1**: The system shall provide a clear and intuitive user interface for learners
- **NFR6.2**: The system shall support multiple interaction modalities including text and voice
- **NFR6.3**: The system shall provide progress indicators and feedback during long operations
- **NFR6.4**: The system shall support accessibility features for users with disabilities
- **NFR6.5**: The system shall provide documentation and help resources for users

## User Requirements

### UR1: Learner Requirements

- **UR1.1**: Learners shall be able to upload and select documents for study
- **UR1.2**: Learners shall receive personalized curricula based on document content
- **UR1.3**: Learners shall interact with the teaching agent through natural conversation
- **UR1.4**: Learners shall complete quizzes and receive immediate feedback
- **UR1.5**: Learners shall view their learning progress and concept mastery levels
- **UR1.6**: Learners shall request clarification or additional examples on any topic
- **UR1.7**: Learners shall control the pace of learning and skip or revisit topics as needed

### UR2: Administrator Requirements

- **UR2.1**: Administrators shall configure system parameters including model selection and resource limits
- **UR2.2**: Administrators shall monitor system performance and resource usage
- **UR2.3**: Administrators shall access logs and analytics for system behavior
- **UR2.4**: Administrators shall manage document libraries and curriculum templates
- **UR2.5**: Administrators shall configure privacy settings and data retention policies

## System Requirements

### SR1: Hardware Requirements

- **SR1.1**: Minimum 8GB RAM for local execution
- **SR1.2**: Minimum 20GB storage for models and document cache
- **SR1.3**: Multi-core CPU (4+ cores recommended) or GPU acceleration support
- **SR1.4**: Network connectivity for optional cloud augmentation and web search

### SR2: Software Requirements

- **SR2.1**: Operating system: Windows, macOS, or Linux
- **SR2.2**: Python runtime environment (version 3.9 or higher)
- **SR2.3**: Support for local LLM inference frameworks
- **SR2.4**: Document processing libraries for PDF and text extraction
- **SR2.5**: Vector database or embedding store for concept indexing

### SR3: Model Requirements

- **SR3.1**: Support for Recursive Language Model (RLM) style hierarchical processing
- **SR3.2**: Support for Energy-Based Model (EBM) constraint validation
- **SR3.3**: Attention-efficient or attentionless inference capabilities
- **SR3.4**: Model quantization support (4-bit or 8-bit) for resource efficiency
- **SR3.5**: Embedding models for concept similarity and retrieval

## Constraints and Assumptions

### Constraints

- **C1**: The system must operate within memory constraints of consumer hardware (8-16GB RAM)
- **C2**: The system must minimize inference latency to maintain interactive teaching experience
- **C3**: The system must respect document copyright and licensing restrictions
- **C4**: The system must avoid generating harmful, biased, or inappropriate content
- **C5**: The system must operate offline for core functionality without internet dependency

### Assumptions

- **A1**: Users have basic computer literacy and can upload documents and interact with a conversational interface
- **A2**: Input documents are primarily educational content (textbooks, papers, tutorials) rather than entertainment or non-instructional material
- **A3**: Learners are motivated to engage with the system and complete assessments honestly
- **A4**: Local hardware has sufficient computational resources to run optimized language models
- **A5**: Document content is primarily text-based; complex multimedia content may have limited support
- **A6**: The system has access to pre-trained models suitable for educational content understanding
- **A7**: Web search augmentation, when used, has access to reliable search APIs or services

## Out of Scope

The following items are explicitly excluded from the current requirements:

- **OS1**: Real-time collaborative learning with multiple simultaneous users
- **OS2**: Integration with institutional learning management systems (LMS) or grade books
- **OS3**: Support for non-text modalities including video lectures, audio content, or interactive simulations
- **OS4**: Automated content creation beyond quizzes (e.g., generating new textbook chapters)
- **OS5**: Social features including peer interaction, discussion forums, or study groups
- **OS6**: Mobile native applications (mobile web access may be supported)
- **OS7**: Advanced analytics and learning science research tools
- **OS8**: Multi-language support beyond English in the initial release
- **OS9**: Integration with external assessment platforms or standardized testing systems
- **OS10**: Gamification features including points, badges, leaderboards, or rewards
- **OS11**: Voice-based interaction as the primary interface (text-first design)
- **OS12**: Custom model training or fine-tuning by end users
